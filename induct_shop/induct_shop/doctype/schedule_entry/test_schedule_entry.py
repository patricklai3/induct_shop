import unittest
import frappe
from induct_shop.tests import test_fixtures
from induct_shop.api.estimation_service import get_total_estimate


class TestScheduleEntry(unittest.TestCase):
    def setUp(self):
        test_fixtures.setup_all()
        self.so_name = test_fixtures.create_test_sales_order(po_no="PO-SE-TEST")
        
        # Ensure Project exists linked to Sales Order and Repair Vehicle
        proj_name = frappe.db.get_value("Project", {"sales_order": self.so_name})
        if not proj_name:
            proj_data = {
                "doctype": "Project",
                "project_name": f"{test_fixtures.PREFIX}Project SE",
                "customer": test_fixtures.CUSTOMER,
                "sales_order": self.so_name,
                "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            }
            if frappe.db.has_column("Project", "custom_repair_vehicle"):
                proj_data["custom_repair_vehicle"] = test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"]
            elif frappe.db.has_column("Project", "repair_vehicle"):
                proj_data["repair_vehicle"] = test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"]
            proj_doc = frappe.get_doc(proj_data).insert(ignore_permissions=True)
            proj_name = proj_doc.name

            frappe.db.set_value("Sales Order", self.so_name, "project", proj_name)

    def tearDown(self):
        test_fixtures.teardown_transactional()

    def test_schedule_entry_auto_population(self):
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "status": "Scheduled"
        })
        se.insert(ignore_permissions=True)

        self.assertTrue(se.name.startswith("SE-"))
        self.assertEqual(se.customer, test_fixtures.CUSTOMER)
        self.assertTrue(bool(se.project))
        self.assertEqual(se.repair_vehicle, test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"])
        self.assertGreater(se.estimated_duration, 0)
        expected_p80 = get_total_estimate([{"item_code": f"{test_fixtures.PREFIX}SERVICE_001", "flat_rate_hours": 1.0}])
        self.assertEqual(se.estimated_duration, expected_p80)
        self.assertIn(f"{test_fixtures.PREFIX}SERVICE_001", se.items_summary)

    def test_so_line_frt_override(self):
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            "customer": test_fixtures.CUSTOMER,
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "items": [
                {
                    "item_code": f"{test_fixtures.PREFIX}SERVICE_001",
                    "qty": 0.18,
                    "uom": "Hour",
                    "stock_uom": "Hour",
                    "conversion_factor": 1.0,
                    "rate": 100
                }
            ]
        }).insert(ignore_permissions=True)

        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": so.name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "10:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # 0.18 hours = 10.8 mins -> P80 (sigma=0.30) is 14 minutes
        self.assertEqual(se.estimated_duration, 14)

    def test_duplicate_sales_order_blocked(self):
        se1 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1"
        })
        se1.insert(ignore_permissions=True)

        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "10:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1"
        })
        with self.assertRaises(frappe.DuplicateEntryError):
            se2.insert(ignore_permissions=True)

    def test_status_transitions(self):
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "09:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
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

    def test_standalone_schedule_entry_creation(self):
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "14:00:00",
            "estimated_duration": 60,
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "John Phone",
            "provisional_vehicle_info": "2021 Model Y",
            "status": "Scheduled"
        })
        se.insert(ignore_permissions=True)

        self.assertTrue(se.name.startswith("SE-"))
        self.assertEqual(se.entry_type, "Diagnostic")
        self.assertIsNone(se.sales_order)
        self.assertIsNone(se.customer)
        self.assertIsNone(se.repair_vehicle)
        self.assertEqual(se.estimated_duration, 60)
        self.assertEqual(se.get_display_customer(), "John Phone")
        self.assertEqual(se.get_display_vehicle(), "2021 Model Y")

    def test_standalone_capacity_conflict(self):
        se1 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "15:00:00",
            "estimated_duration": 60,
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "Alice",
            "status": "Scheduled"
        })
        se1.insert(ignore_permissions=True)

        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "15:30:00",
            "estimated_duration": 60,
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "Bob",
            "status": "Scheduled"
        })
        with self.assertRaises(frappe.ValidationError):
            se2.insert(ignore_permissions=True)

    def test_display_helper_fallbacks(self):
        # 1. Fully empty links and quick-entry fields -> Guest / ""
        se_empty = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "16:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
        })
        self.assertEqual(se_empty.get_display_customer(), "Guest")
        self.assertEqual(se_empty.get_display_vehicle(), "")

        # 2. Provisional quick entry fields set
        se_prov = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "16:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "Charlie",
            "provisional_vehicle_info": "2022 F-150",
        })
        self.assertEqual(se_prov.get_display_customer(), "Charlie")
        self.assertEqual(se_prov.get_display_vehicle(), "2022 F-150")

        # 3. Master records set
        se_master = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Repair",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "16:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "Charlie",
            "provisional_vehicle_info": "2022 F-150",
        })
        se_master.populate_from_sales_order()
        self.assertEqual(se_master.get_display_customer(), test_fixtures.CUSTOMER)
        self.assertTrue(len(se_master.get_display_vehicle()) > 0)

    def test_schedule_entry_type_records(self):
        """Test creation and existence of Schedule Entry Type records."""
        self.assertTrue(frappe.db.exists("Schedule Entry Type", "Diagnostic"))
        self.assertTrue(frappe.db.exists("Schedule Entry Type", "Repair"))
        diag_type = frappe.get_doc("Schedule Entry Type", "Diagnostic")
        self.assertEqual(diag_type.requires_sales_order, 0)
        repair_type = frappe.get_doc("Schedule Entry Type", "Repair")
        self.assertEqual(repair_type.requires_sales_order, 1)

    def test_vehicle_check_in_linkage(self):
        """Test Vehicle Check-in linkage and automatic project cross-referencing to originating Schedule Entry."""
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Diagnostic",
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "17:00:00",
            "estimated_duration": 45,
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "provisional_customer_name": "Test Intake Cust",
            "provisional_vehicle_info": "Test Intake Veh",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        vci = test_fixtures.create_test_vehicle_check_in(
            customer=test_fixtures.CUSTOMER,
            vehicle=test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"],
            schedule_entry=se.name
        )

        se.reload()
        self.assertEqual(se.project, vci.project)
        self.assertEqual(se.repair_vehicle, test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"])
        self.assertEqual(se.customer, test_fixtures.CUSTOMER)
        self.assertEqual(se.vehicle_check_in, vci.name)

    def test_repair_entry_with_sales_order(self):
        """Test Sales Order creation and linking for repair entries."""
        se = frappe.get_doc({
            "doctype": "Schedule Entry",
            "entry_type": "Repair",
            "sales_order": self.so_name,
            "scheduled_date": frappe.utils.today(),
            "scheduled_time": "18:00:00",
            "service_bay": f"{test_fixtures.PREFIX}Bay 1",
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        self.assertEqual(se.entry_type, "Repair")
        self.assertEqual(se.sales_order, self.so_name)
        self.assertEqual(se.customer, test_fixtures.CUSTOMER)
        self.assertEqual(se.repair_vehicle, test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"])
        self.assertTrue(se.estimated_duration > 0)


if __name__ == "__main__":
    unittest.main()



