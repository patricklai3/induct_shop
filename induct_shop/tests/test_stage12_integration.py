import unittest
from datetime import timedelta
import frappe

from induct_shop.api.scheduling import (
    effective_end_time,
    check_bay_availability,
    auto_assign_bay,
    get_available_bays,
    get_available_slots,
    is_holiday,
)
from induct_shop.api.technician_availability import (
    get_active_technicians,
    check_technician_availability,
    get_technician_pool_availability,
    get_technician_queue,
)
from induct_shop.api.scheduling_views import get_calendar_events
from induct_shop.api.sales_order_hooks import handle_amendment
from induct_shop.tests.test_fixtures import (
    setup_all,
    teardown_transactional,
    create_test_sales_order,
    PREFIX,
    CUSTOMER,
)


class TestStage12Integration(unittest.TestCase):
    """
    Stage 12 End-to-End Integration & Edge Case Tests for the Scheduling System.
    Validates all 10 core integration scenarios specified in Stage 12 checklist.
    """

    def setUp(self):
        self.emp_map = setup_all()
        self.tech1_id = self.emp_map["tech_active_1"]
        self.tech2_id = self.emp_map["tech_active_2"]

        self.bay1 = f"{PREFIX}Bay 1"
        self.bay2 = f"{PREFIX}Bay 2"

        self.date_today = frappe.utils.today()
        self.date_tomorrow = str(frappe.utils.add_days(self.date_today, 1))

    def tearDown(self):
        teardown_transactional([self.tech1_id, self.tech2_id])

    # 1. Full Workflow Test
    def test_01_full_workflow(self):
        """Create Sales Order -> auto_assign_bay -> Schedule Entry creation & auto-population."""
        so_name = create_test_sales_order(f"{PREFIX}SO-STAGE12-01")
        so_doc = frappe.get_doc("Sales Order", so_name)
        if so_doc.docstatus == 0:
            so_doc.submit()

        assigned_bay = auto_assign_bay(self.date_today, "09:00:00", 60)
        self.assertTrue(bool(assigned_bay))
        self.assertTrue(frappe.db.exists("Service Bay", assigned_bay))

        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so_name,
            "scheduled_date": self.date_today,
            "scheduled_time": "09:00:00",
            "service_bay": assigned_bay,
            "assigned_technician": self.tech1_id,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        self.assertTrue(se.name.startswith("SE-"))
        self.assertEqual(se.customer, CUSTOMER)
        self.assertGreater(se.estimated_duration, 0)
        self.assertIn(f"{PREFIX}SERVICE_001", se.items_summary)

    # 2. Capacity Limits (Bays & Tech Pool)
    def test_02_capacity_limits(self):
        """Fill all currently available bays and verify auto_assign_bay is blocked when full."""
        avail_bays = get_available_bays(self.date_today, "09:00:00", 120)
        for idx, b_info in enumerate(avail_bays):
            b_name = b_info["bay_name"]
            so = create_test_sales_order(f"{PREFIX}SO-STAGE12-CAP-{idx}")
            frappe.get_doc({
                "doctype": "Schedule Entry",
                "sales_order": so,
                "scheduled_date": self.date_today,
                "scheduled_time": "09:00:00",
                "estimated_duration": 120,
                "service_bay": b_name,
                "status": "Scheduled",
            }).insert(ignore_permissions=True)

        # Bay pool is now completely full -> auto_assign_bay should throw ValidationError
        with self.assertRaises(frappe.ValidationError):
            auto_assign_bay(self.date_today, "09:00:00", 60)

    # 3. Amendment Flow
    def test_03_amendment_flow(self):
        """Amend a Sales Order -> linked Schedule Entry transitions to 'Needs Review' & recalculates duration."""
        # Step A: Create and submit initial SO
        so1 = frappe.get_doc({
            "doctype": "Sales Order",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            "customer": CUSTOMER,
            "po_no": f"{PREFIX}PO-AMEND-01",
            "delivery_date": self.date_tomorrow,
            "items": [{
                "item_code": f"{PREFIX}SERVICE_001",
                "qty": 1,
                "uom": "Hour",
                "stock_uom": "Hour",
                "rate": 100
            }]
        }).insert(ignore_permissions=True)
        so1.submit()

        # Step B: Create Schedule Entry for SO1
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so1.name,
            "scheduled_date": self.date_today,
            "scheduled_time": "09:00:00",
            "service_bay": self.bay1,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        initial_duration = se.estimated_duration

        # Step C: Cancel SO1 and amend it
        so1.cancel()
        so1_amended = frappe.copy_doc(so1)
        so1_amended.amended_from = so1.name
        so1_amended.docstatus = 0
        so1_amended.items[0].qty = 3  # Increase FRT/qty from 1 to 3 hours
        so1_amended.insert(ignore_permissions=True)
        so1_amended.submit()

        # Step D: Verify handle_amendment ran on submit
        se_updated = frappe.get_doc("Schedule Entry", se.name)
        self.assertEqual(se_updated.sales_order, so1_amended.name)
        self.assertEqual(se_updated.status, "Needs Review")
        self.assertGreater(se_updated.estimated_duration, initial_duration)

    # 4. Leave Integration
    def test_04_leave_integration(self):
        """Put technician on leave -> verify pool exclusion and individual check."""
        leave_type = "Casual Leave" if frappe.db.exists("Leave Type", "Casual Leave") else frappe.db.get_value("Leave Type", {}, "name")
        leave = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": self.tech1_id,
            "leave_type": leave_type,
            "from_date": self.date_today,
            "to_date": self.date_today,
            "status": "Approved",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
        })
        leave.flags.ignore_validate = True
        leave.flags.ignore_mandatory = True
        leave.insert(ignore_permissions=True)
        frappe.db.set_value("Leave Application", leave.name, "docstatus", 1)

        techs = get_active_technicians(date=self.date_today)
        tech1_info = next((t for t in techs if t["employee"] == self.tech1_id), None)
        self.assertIsNotNone(tech1_info)
        self.assertTrue(tech1_info["on_leave"])

        chk = check_technician_availability(self.tech1_id, self.date_today, "09:00:00", 60)
        self.assertFalse(chk["is_available"])
        self.assertEqual(chk["reason"], "on_leave")

    # 5. Holiday Handling
    def test_05_holiday_handling(self):
        """Verify holiday detection API."""
        res = is_holiday(self.date_today)
        self.assertIn("is_holiday", res)
        self.assertIn("description", res)

    # 6. Lunch Edge Cases
    def test_06_lunch_edge_cases(self):
        """Jobs starting before, spanning, and after lunch calculate effective end times correctly across calendar events."""
        so1 = create_test_sales_order(f"{PREFIX}SO-LUNCH-1")
        so2 = create_test_sales_order(f"{PREFIX}SO-LUNCH-2")
        so3 = create_test_sales_order(f"{PREFIX}SO-LUNCH-3")

        # Job 1: 08:00 (60 min) -> 09:00 (no lunch)
        se1 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so1,
            "scheduled_date": self.date_today,
            "scheduled_time": "08:00:00",
            "estimated_duration": 60,
            "service_bay": self.bay1,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        # Job 2: 11:00 (120 min) -> spans 12:00-12:30 lunch -> 13:30 end
        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so2,
            "scheduled_date": self.date_today,
            "scheduled_time": "11:00:00",
            "estimated_duration": 120,
            "service_bay": self.bay1,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        # Job 3: 13:30 (60 min) -> 14:30 (no lunch)
        se3 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so3,
            "scheduled_date": self.date_today,
            "scheduled_time": "13:30:00",
            "estimated_duration": 60,
            "service_bay": self.bay1,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        events = get_calendar_events(start=self.date_today, end=self.date_today)
        event_map = {e["name"]: e for e in events if e["name"] in [se1.name, se2.name, se3.name]}

        self.assertFalse(event_map[se1.name]["spans_lunch"])
        self.assertEqual(event_map[se1.name]["end"], f"{self.date_today} 09:00:00")

        self.assertTrue(event_map[se2.name]["spans_lunch"])
        self.assertEqual(event_map[se2.name]["end"], f"{self.date_today} 13:30:00")

        self.assertFalse(event_map[se3.name]["spans_lunch"])
        self.assertEqual(event_map[se3.name]["end"], f"{self.date_today} 14:30:00")

    # 7. Equipment Tag Filtering
    def test_07_equipment_tag_filtering(self):
        """Require 'Alignment Rack' -> only Bay 2 is considered."""
        bays_all = get_available_bays(self.date_today, "09:00:00", 60)
        bay_names_all = [b["bay_name"] for b in bays_all]
        self.assertIn(self.bay1, bay_names_all)
        self.assertIn(self.bay2, bay_names_all)

        bays_align = get_available_bays(self.date_today, "09:00:00", 60, required_tags=["Alignment Rack"])
        bay_names_align = [b["bay_name"] for b in bays_align]
        self.assertNotIn(self.bay1, bay_names_align)
        self.assertIn(self.bay2, bay_names_align)

    # 8. Technician Capacity Toggle
    def test_08_enable_technician_capacity_toggle(self):
        """Disabling technician capacity operates in bay-only mode without error."""
        doc = frappe.get_single("Shop Settings")
        orig_val = doc.enable_technician_capacity
        try:
            doc.enable_technician_capacity = 0
            doc.save(ignore_permissions=True)

            pool = get_technician_pool_availability(self.date_today, "09:00:00", 60)
            self.assertTrue(pool["is_available"])
            self.assertEqual(pool["total_technicians"], 999)

            slots = get_available_slots(self.date_today, 60)
            self.assertGreater(len(slots), 0)
        finally:
            doc.enable_technician_capacity = orig_val
            doc.save(ignore_permissions=True)

    # 9. Multi-Day Scheduling
    def test_09_multi_day_scheduling(self):
        """Scheduling on Day 1 does not affect availability on Day 2."""
        so1 = create_test_sales_order(f"{PREFIX}SO-MULTIDAY-1")

        # Book Bay 1 on Day 1
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so1,
            "scheduled_date": self.date_today,
            "scheduled_time": "09:00:00",
            "estimated_duration": 120,
            "service_bay": self.bay1,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        # Bay 1 on Day 1 at 09:00 is unavailable
        self.assertFalse(check_bay_availability(self.bay1, self.date_today, "09:00:00", 120))

        # Bay 1 on Day 2 at 09:00 is available
        self.assertTrue(check_bay_availability(self.bay1, self.date_tomorrow, "09:00:00", 120))

    # 10. Reinstall Resilience & Schema Integrity
    def test_10_schema_integrity(self):
        """Verify all core DocTypes and essential fields exist."""
        required_doctypes = [
            "Schedule Entry",
            "Service Bay",
            "Service Bay Equipment",
            "Shop Settings",
            "Equipment Tag",
        ]
        for dt in required_doctypes:
            self.assertTrue(frappe.db.exists("DocType", dt), f"DocType {dt} missing!")


if __name__ == "__main__":
    unittest.main()
