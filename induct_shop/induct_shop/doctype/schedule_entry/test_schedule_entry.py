import unittest
import frappe
from induct_shop.api.estimation_service import get_total_estimate


class TestScheduleEntry(unittest.TestCase):
    def setUp(self):
        # 1. Ensure test Service Bay exists
        if not frappe.db.exists("Service Bay", "Test Schedule Bay"):
            frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": "Test Schedule Bay",
                "is_active": 1,
                "description": "Bay for testing Schedule Entry"
            }).insert(ignore_permissions=True)

        # 2. Ensure test Customer exists
        if not frappe.db.exists("Customer", "_Test Schedule Customer"):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "_Test Schedule Customer",
                "customer_group": "Commercial",
                "territory": "All Territories"
            }).insert(ignore_permissions=True)

        # 3. Ensure test Item exists with custom_frt
        if not frappe.db.exists("Item", "_Test Service Item 01"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "_Test Service Item 01",
                "item_name": "Test Service Operation",
                "item_group": "Services",
                "is_stock_item": 0,
            })
            if frappe.db.has_column("Item", "custom_frt"):
                item.custom_frt = 60.0
            item.insert(ignore_permissions=True)

        # 4. Ensure test Repair Vehicle exists
        if not frappe.db.exists("Repair Vehicle", "TEST-VIN-SCHED-01"):
            frappe.get_doc({
                "doctype": "Repair Vehicle",
                "vin": "TEST-VIN-SCHED-01",
                "make": "Tesla",
                "model": "Model Y",
                "year": 2023,
                "customer": "_Test Schedule Customer"
            }).insert(ignore_permissions=True)

        # 5. Ensure test Project exists linked to Repair Vehicle
        proj_name = frappe.db.get_value("Project", {"project_name": "_Test Schedule Project"})
        if not proj_name:
            proj_data = {
                "doctype": "Project",
                "project_name": "_Test Schedule Project",
                "customer": "_Test Schedule Customer",
            }
            if frappe.db.has_column("Project", "custom_repair_vehicle"):
                proj_data["custom_repair_vehicle"] = "TEST-VIN-SCHED-01"
            elif frappe.db.has_column("Project", "repair_vehicle"):
                proj_data["repair_vehicle"] = "TEST-VIN-SCHED-01"
            proj_doc = frappe.get_doc(proj_data).insert(ignore_permissions=True)
            proj_name = proj_doc.name

        # 6. Ensure test Sales Order exists
        so_name = frappe.db.get_value("Sales Order", {"customer": "_Test Schedule Customer"})
        if not so_name:
            so = frappe.get_doc({
                "doctype": "Sales Order",
                "company": "_Test Company" if frappe.db.exists("Company", "_Test Company") else frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
                "customer": "_Test Schedule Customer",
                "project": proj_name,
                "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
                "items": [
                    {
                        "item_code": "_Test Service Item 01",
                        "qty": 1,
                        "rate": 100
                    }
                ]
            })
            so.insert(ignore_permissions=True)
            so_name = so.name
        self.so_name = so_name

    def tearDown(self):
        if hasattr(self, "so_name"):
            frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE sales_order=%s", self.so_name)
            frappe.db.commit()

    def test_schedule_entry_auto_population(self):
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": "Test Schedule Bay",
            "status": "Scheduled"
        })
        se.insert(ignore_permissions=True)

        self.assertTrue(se.name.startswith("SE-"))
        self.assertEqual(se.customer, "_Test Schedule Customer")
        self.assertTrue(bool(se.project))
        self.assertEqual(se.repair_vehicle, "TEST-VIN-SCHED-01")
        self.assertGreater(se.estimated_duration, 0)
        expected_p80 = get_total_estimate(["_Test Service Item 01"])
        self.assertEqual(se.estimated_duration, expected_p80)
        self.assertIn("_Test Service Item 01", se.items_summary)

    def test_duplicate_sales_order_blocked(self):
        se1 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": "Test Schedule Bay"
        })
        se1.insert(ignore_permissions=True)

        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "10:00:00",
            "service_bay": "Test Schedule Bay"
        })
        with self.assertRaises(frappe.DuplicateEntryError):
            se2.insert(ignore_permissions=True)

    def test_status_transitions(self):
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": "Test Schedule Bay",
            "status": "Scheduled"
        })
        se.insert(ignore_permissions=True)

        self.assertEqual(se.status, "Scheduled")

        se.status = "In Progress"
        se.save(ignore_permissions=True)
        self.assertEqual(frappe.db.get_value("Schedule Entry", se.name, "status"), "In Progress")

        se.status = "Completed"
        se.save(ignore_permissions=True)
        self.assertEqual(frappe.db.get_value("Schedule Entry", se.name, "status"), "Completed")


if __name__ == "__main__":
    unittest.main()
