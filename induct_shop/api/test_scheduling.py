import unittest
from datetime import timedelta
import frappe
from induct_shop.api.scheduling import (
    effective_end_time,
    check_bay_availability,
    auto_assign_bay,
    get_available_bays,
    get_available_slots,
    to_timedelta,
    format_timedelta,
)


class TestSchedulingApi(unittest.TestCase):
    def setUp(self):
        # 1. Create equipment tags if needed
        for tag in ["Lift", "Alignment Rack", "HV Battery Station"]:
            if not frappe.db.exists("Equipment Tag", tag):
                frappe.get_doc({
                    "doctype": "Equipment Tag",
                    "tag_name": tag,
                }).insert(ignore_permissions=True)

        # 2. Setup test Service Bays
        # Bay 1: has "Lift"
        if not frappe.db.exists("Service Bay", "Test Bay 1"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Bay 1",
                "is_active": 1,
                "description": "General service bay",
                "equipment": [{"equipment_tag": "Lift"}]
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Bay 1", "is_active", 1)

        # Bay 2: has "Lift" and "Alignment Rack"
        if not frappe.db.exists("Service Bay", "Test Bay 2"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Bay 2",
                "is_active": 1,
                "description": "Alignment bay",
                "equipment": [{"equipment_tag": "Lift"}, {"equipment_tag": "Alignment Rack"}]
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Bay 2", "is_active", 1)

        # Bay 3: inactive bay
        if not frappe.db.exists("Service Bay", "Test Bay Inactive"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Bay Inactive",
                "is_active": 0,
                "description": "Inactive bay",
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Bay Inactive", "is_active", 0)

        # 3. Clean up test Schedule Entries
        frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE 'Test Bay%'")
        frappe.db.commit()

        # Ensure UOM "Hour" exists
        if not frappe.db.exists("UOM", "Hour"):
            frappe.get_doc({"doctype": "UOM", "uom_name": "Hour"}).insert(ignore_permissions=True)

        # Ensure _Test Service Item 01 has Hour in its uoms child table
        if frappe.db.exists("Item", "_Test Service Item 01"):
            item_doc = frappe.get_doc("Item", "_Test Service Item 01")
            has_uom = any(u.uom == "Hour" for u in item_doc.uoms)
            if not has_uom:
                item_doc.append("uoms", {"uom": "Hour", "conversion_factor": 1.0})
                item_doc.save(ignore_permissions=True)

        # 4. Ensure test Sales Orders exist for Schedule Entries
        if not frappe.db.exists("Customer", "_Test Scheduling Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "_Test Scheduling Customer",
                "customer_group": "Commercial",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)


        self.test_so1 = self._get_or_create_sales_order("_Test Scheduling Customer", "SO-SCHED-01")
        self.test_so2 = self._get_or_create_sales_order("_Test Scheduling Customer", "SO-SCHED-02")
        self.test_so3 = self._get_or_create_sales_order("_Test Scheduling Customer", "SO-SCHED-03")

    def _get_or_create_sales_order(self, customer, name_suffix):
        so_name = frappe.db.get_value("Sales Order", {"customer": customer, "po_no": name_suffix})
        if not so_name:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
                "customer": customer,
                "po_no": name_suffix,
                "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
                "items": [{
                    "item_code": "_Test Service Item 01" if frappe.db.exists("Item", "_Test Service Item 01") else frappe.db.get_value("Item", {}, "name"),
                    "qty": 1,
                    "rate": 100
                }]
            }).insert(ignore_permissions=True)
            so_name = so.name
        return so_name

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE 'Test Bay%'")
        frappe.db.commit()

    # --- 1. Lunch-Aware Time Window Tests ---
    def test_effective_end_time_before_lunch(self):
        # 08:00 start, 120 min -> 10:00 end (no lunch adjustment)
        eff_end = effective_end_time("08:00:00", 120, break_start="12:00:00", break_end="12:30:00")
        self.assertEqual(eff_end, timedelta(hours=10))

    def test_effective_end_time_spanning_lunch(self):
        # 11:00 start, 120 min -> naive 13:00, spans 12:00 break -> effective end 13:30 (+30 min break)
        eff_end = effective_end_time("11:00:00", 120, break_start="12:00:00", break_end="12:30:00")
        self.assertEqual(eff_end, timedelta(hours=13, minutes=30))

    def test_effective_end_time_after_lunch(self):
        # 13:00 start, 90 min -> 14:30 end (no lunch adjustment)
        eff_end = effective_end_time("13:00:00", 90, break_start="12:00:00", break_end="12:30:00")
        self.assertEqual(eff_end, timedelta(hours=14, minutes=30))

    # --- 2. Bay Overlap & Availability Tests ---
    def test_bay_availability_no_conflict(self):
        date = frappe.utils.today()
        # Create an entry from 08:00 to 10:00 (120 mins)
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Check 10:00 to 12:00 -> should be available
        avail = check_bay_availability("Test Bay 1", date, "10:00:00", 120)
        self.assertTrue(avail)

        # Check different bay at 08:00 -> should be available
        avail_bay2 = check_bay_availability("Test Bay 2", date, "08:00:00", 120)
        self.assertTrue(avail_bay2)

    def test_bay_availability_overlap_blocked(self):
        date = frappe.utils.today()
        # Entry 1: 08:00 to 10:00
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Overlapping attempt: 09:00 to 11:00
        avail = check_bay_availability("Test Bay 1", date, "09:00:00", 120)
        self.assertFalse(avail)

        # Schedule Entry controller should throw ValidationError on insert
        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so2,
            "scheduled_date": date,
            "scheduled_time": "09:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 1",
            "status": "Scheduled"
        })
        with self.assertRaises(frappe.ValidationError):
            se2.insert(ignore_permissions=True)

    def test_bay_availability_rescheduling_self_exclusion(self):
        date = frappe.utils.today()
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Excluding self should show bay as available
        avail = check_bay_availability("Test Bay 1", date, "08:00:00", 120, exclude_entry=se.name)
        self.assertTrue(avail)

        # Updating the entry to same slot should succeed without self-conflict error
        se.notes = "Updated notes"
        se.save(ignore_permissions=True)

    # --- 3. Auto-Assign Bay Tests ---
    def test_auto_assign_bay(self):
        date = frappe.utils.today()
        # Bay 1 and Bay 2 are free. Both have "Lift".
        assigned = auto_assign_bay(date, "08:00:00", 60, required_tags=["Lift"])
        self.assertIn(assigned, ["Test Bay 1", "Test Bay 2"])

        # Require "Alignment Rack" -> only Test Bay 2 has it
        assigned_align = auto_assign_bay(date, "08:00:00", 60, required_tags=["Alignment Rack"])
        self.assertEqual(assigned_align, "Test Bay 2")

    def test_auto_assign_bay_no_capacity_raises(self):
        date = frappe.utils.today()

        # Book Test Bay 2 (which is the only bay with "Alignment Rack")
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 2",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Attempt to auto assign at 08:30 requiring "Alignment Rack" -> Test Bay 2 is occupied
        with self.assertRaises(frappe.ValidationError):
            auto_assign_bay(date, "08:30:00", 60, required_tags=["Alignment Rack"])


    # --- 4. Available Slots Tests ---
    def test_get_available_slots(self):
        date = frappe.utils.today()

        # Fetch slots for 60-minute duration
        slots = get_available_slots(date, 60)

        # Check lunch slots (12:00) are excluded
        slot_times = [s["start_time"] for s in slots]
        self.assertNotIn("12:00", slot_times)

        # Check slot structure
        if slots:
            slot = slots[0]
            self.assertIn("start_time", slot)
            self.assertIn("available_bays", slot)
            self.assertGreater(slot["available_bays"], 0)

    def test_get_available_slots_with_occupied_bay(self):
        date = frappe.utils.today()

        # Book Test Bay 1 at 08:00:00 for 120 min
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Check slots specific to Test Bay 1
        bay1_slots = get_available_slots(date, 60, service_bay="Test Bay 1")
        bay1_times = [s["start_time"] for s in bay1_slots]
        self.assertNotIn("08:00", bay1_times)
        self.assertNotIn("08:30", bay1_times)
        self.assertNotIn("09:00", bay1_times)
        self.assertNotIn("09:30", bay1_times)
        self.assertIn("10:00", bay1_times)


if __name__ == "__main__":
    unittest.main()
