import unittest
from datetime import timedelta
import frappe

from induct_shop.api.scheduling import (
    get_available_slots,
    auto_assign_bay,
    get_shop_settings,
)
from induct_shop.api.technician_availability import (
    get_active_technicians,
    get_technician_pool_availability,
    check_technician_availability,
    get_technician_queue,
    get_daily_technician_overview,
)


class TestTechnicianAvailabilityApi(unittest.TestCase):
    def setUp(self):
        # 1. Ensure Shop Settings exists and has default values
        if frappe.db.exists("DocType", "Shop Settings"):
            doc = frappe.get_single("Shop Settings")
            doc.technician_designation = "Technician"
            doc.enable_technician_capacity = 1
            doc.save(ignore_permissions=True)

        # 2. Ensure Designation "Technician" exists
        if not frappe.db.exists("Designation", "Technician"):
            frappe.get_doc({
                "doctype": "Designation",
                "designation_name": "Technician",
            }).insert(ignore_permissions=True)

        company = frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC"

        # 3. Create test Employees
        # Tech 1: Active
        self.tech1_id = frappe.db.get_value("Employee", {"first_name": "Tech", "last_name": "One", "status": "Active"})
        if not self.tech1_id:
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": "Tech",
                "last_name": "One",
                "employee_name": "Tech One",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": "2020-01-01",
                "status": "Active",
                "designation": "Technician",
                "company": company,
            }).insert(ignore_permissions=True)
            self.tech1_id = doc.name

        # Tech 2: Active
        self.tech2_id = frappe.db.get_value("Employee", {"first_name": "Tech", "last_name": "Two", "status": "Active"})
        if not self.tech2_id:
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": "Tech",
                "last_name": "Two",
                "employee_name": "Tech Two",
                "gender": "Female",
                "date_of_birth": "1992-02-02",
                "date_of_joining": "2021-01-01",
                "status": "Active",
                "designation": "Technician",
                "company": company,
            }).insert(ignore_permissions=True)
            self.tech2_id = doc.name

        # Tech 3: Inactive
        self.tech3_id = frappe.db.get_value("Employee", {"first_name": "Tech", "last_name": "Three", "status": "Left"})
        if not self.tech3_id:
            doc = frappe.get_doc({
                "doctype": "Employee",
                "first_name": "Tech",
                "last_name": "Three",
                "employee_name": "Tech Three",
                "gender": "Male",
                "date_of_birth": "1988-03-03",
                "date_of_joining": "2019-01-01",
                "relieving_date": "2022-01-01",
                "status": "Left",
                "designation": "Technician",
                "company": company,
            }).insert(ignore_permissions=True)
            self.tech3_id = doc.name

        # 4. Ensure test Service Bays exist
        if not frappe.db.exists("Service Bay", "Test Tech Bay 1"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Tech Bay 1",
                "is_active": 1,
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Tech Bay 1", "is_active", 1)

        if not frappe.db.exists("Service Bay", "Test Tech Bay 2"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Tech Bay 2",
                "is_active": 1,
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Tech Bay 2", "is_active", 1)

        if not frappe.db.exists("Service Bay", "Test Tech Bay 3"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Tech Bay 3",
                "is_active": 1,
            }).insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Service Bay", "Test Tech Bay 3", "is_active", 1)

        # Clean up test Schedule Entries and Leave Applications
        frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE 'Test Tech Bay%'")
        frappe.db.sql("DELETE FROM `tabLeave Application` WHERE employee IN (%s, %s, %s)", (self.tech1_id, self.tech2_id, self.tech3_id))
        frappe.db.commit()

        # 5. Ensure test Sales Orders exist
        if not frappe.db.exists("Customer", "_Test Tech Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "_Test Tech Customer",
                "customer_group": "Commercial",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)

        self.test_so1 = self._get_or_create_sales_order("_Test Tech Customer", "SO-TECH-01")
        self.test_so2 = self._get_or_create_sales_order("_Test Tech Customer", "SO-TECH-02")
        self.test_so3 = self._get_or_create_sales_order("_Test Tech Customer", "SO-TECH-03")

    def _get_or_create_sales_order(self, customer, po_no):
        so_name = frappe.db.get_value("Sales Order", {"customer": customer, "po_no": po_no})
        if not so_name:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
                "customer": customer,
                "po_no": po_no,
                "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
                "items": [{
                    "item_code": frappe.db.get_value("Item", {}, "name"),
                    "qty": 1,
                    "rate": 100
                }]
            }).insert(ignore_permissions=True)
            so_name = so.name
        return so_name

    def tearDown(self):
        frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE 'Test Tech Bay%'")
        frappe.db.sql("DELETE FROM `tabLeave Application` WHERE employee IN (%s, %s, %s)", (self.tech1_id, self.tech2_id, self.tech3_id))
        frappe.db.commit()

    # --- 1. Roster Test ---
    def test_get_active_technicians(self):
        techs = get_active_technicians()
        emp_names = [t["employee"] for t in techs]

        self.assertIn(self.tech1_id, emp_names)
        self.assertIn(self.tech2_id, emp_names)
        self.assertNotIn(self.tech3_id, emp_names)  # Inactive status

    # --- 2. Leave Integration Test ---
    def test_leave_application_integration(self):
        date = frappe.utils.today()

        # Create approved Leave Application for Tech 1
        leave = frappe.get_doc({
            "doctype": "Leave Application",
            "employee": self.tech1_id,
            "leave_type": "Casual Leave" if frappe.db.exists("Leave Type", "Casual Leave") else frappe.db.get_value("Leave Type", {}, "name"),
            "from_date": date,
            "to_date": date,
            "status": "Approved",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
        })
        leave.flags.ignore_validate = True
        leave.flags.ignore_mandatory = True
        leave.insert(ignore_permissions=True)
        frappe.db.set_value("Leave Application", leave.name, "docstatus", 1)
        frappe.db.set_value("Leave Application", leave.name, "status", "Approved")

        techs = get_active_technicians(date=date)
        tech1 = next(t for t in techs if t["employee"] == self.tech1_id)
        tech2 = next(t for t in techs if t["employee"] == self.tech2_id)

        self.assertTrue(tech1["on_leave"])
        self.assertFalse(tech2["on_leave"])

        # Check individual technician availability
        chk = check_technician_availability(self.tech1_id, date, "08:00:00", 60)
        self.assertFalse(chk["is_available"])
        self.assertEqual(chk["reason"], "on_leave")


    # --- 3. Pool Gating Test ---
    def test_pool_gating_capacity(self):
        date = frappe.utils.today()

        # Check initial pool availability at 08:00
        pool_init = get_technician_pool_availability(date, "08:00:00", 120)
        self.assertTrue(pool_init["is_available"])

        # Create Schedule Entries for all active technicians at 08:00 on date
        active_techs = get_active_technicians(date=date)
        on_duty_techs = [t["employee"] for t in active_techs if not t["on_leave"]]

        # Fill all on-duty technicians
        for idx, tech_id in enumerate(on_duty_techs):
            bay_name = f"Test Tech Bay Pool {idx + 1}"
            if not frappe.db.exists("Service Bay", bay_name):
                frappe.get_doc({
                    "doctype": "Service Bay",
                    "bay_name": bay_name,
                    "is_active": 1,
                }).insert(ignore_permissions=True)
            else:
                frappe.db.set_value("Service Bay", bay_name, "is_active", 1)
            so_name = self._get_or_create_sales_order("_Test Tech Customer", f"SO-TECH-POOL-{idx}")
            frappe.get_doc({
                "doctype": "Schedule Entry",
                "sales_order": so_name,
                "scheduled_date": date,
                "scheduled_time": "08:00:00",
                "estimated_duration": 120,
                "service_bay": bay_name,
                "assigned_technician": tech_id,
                "status": "Scheduled",
            }).insert(ignore_permissions=True)



        # Now all active techs are occupied at 08:00
        pool = get_technician_pool_availability(date, "08:00:00", 120)
        self.assertFalse(pool["is_available"])
        self.assertEqual(pool["available"], 0)

        # Creating another Schedule Entry without a technician when pool is full should be blocked
        # Need a fresh sales order so unique constraint on sales_order doesn't fail
        extra_so = self._get_or_create_sales_order("_Test Tech Customer", "SO-TECH-EXTRA")
        se_extra = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": extra_so,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Tech Bay 1",
            "status": "Scheduled",
        })
        with self.assertRaises(frappe.ValidationError):
            se_extra.insert(ignore_permissions=True)

    def test_pool_gating_disabled_toggle(self):
        date = frappe.utils.today()

        # Turn off enable_technician_capacity
        doc = frappe.get_single("Shop Settings")
        doc.enable_technician_capacity = 0
        doc.save(ignore_permissions=True)

        try:
            pool = get_technician_pool_availability(date, "08:00:00", 120)
            self.assertTrue(pool["is_available"])
            self.assertEqual(pool["total_technicians"], 999)
        finally:
            # Re-enable
            doc.enable_technician_capacity = 1
            doc.save(ignore_permissions=True)

    # --- 4. Individual Overlap Soft Warning Test ---
    def test_individual_technician_overlap_soft_warning(self):
        date = frappe.utils.today()

        # Book Tech 1 at 08:00:00
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": "Test Tech Bay 1",
            "assigned_technician": self.tech1_id,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        chk = check_technician_availability(self.tech1_id, date, "08:30:00", 60)
        self.assertFalse(chk["is_available"])
        self.assertEqual(chk["reason"], "overlap")
        self.assertEqual(len(chk["conflicts"]), 1)

    # --- 5. Dual-Resource Available Slots Test ---
    def test_dual_resource_available_slots(self):
        date = frappe.utils.today()

        slots = get_available_slots(date, 60)
        self.assertTrue(len(slots) > 0)

        slot = slots[0]
        self.assertIn("available_bays", slot)
        self.assertIn("available_technicians", slot)
        self.assertIn("effective_capacity", slot)
        self.assertEqual(
            slot["effective_capacity"],
            min(slot["available_bays"], slot["available_technicians"])
        )

    # --- 6. Work Queue Test ---
    def test_get_technician_queue(self):
        date = frappe.utils.today()

        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 60,
            "service_bay": "Test Tech Bay 1",
            "assigned_technician": self.tech1_id,
            "status": "Scheduled",
        }).insert(ignore_permissions=True)

        queue = get_technician_queue(self.tech1_id, date)
        self.assertEqual(queue["employee"], self.tech1_id)
        self.assertEqual(queue["total_jobs"], 1)
        self.assertEqual(queue["total_minutes"], 60)
        self.assertGreater(queue["utilization_pct"], 0)

    # --- 7. Daily Overview Test ---
    def test_get_daily_technician_overview(self):
        date = frappe.utils.today()

        overview = get_daily_technician_overview(date)
        self.assertEqual(overview["date"], date)
        self.assertIn("technicians", overview)
        self.assertIn("shop_summary", overview)


if __name__ == "__main__":
    unittest.main()
