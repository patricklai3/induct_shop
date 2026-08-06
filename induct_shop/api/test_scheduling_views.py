import unittest
from datetime import timedelta
import frappe
from induct_shop.api.scheduling_views import get_calendar_events, STATUS_COLOR_MAP
from induct_shop.tests.test_fixtures import setup_all, teardown_transactional, create_test_sales_order, PREFIX


class TestSchedulingViewsApi(unittest.TestCase):
    def setUp(self):
        self.emp_map = setup_all()
        self.bay1 = f"{PREFIX}Bay 1"
        self.test_so1 = create_test_sales_order(f"{PREFIX}SO-VIEW-01")
        self.test_so2 = create_test_sales_order(f"{PREFIX}SO-VIEW-02")

    def tearDown(self):
        teardown_transactional(self.emp_map.values())

    def test_get_calendar_events_structure_and_lunch_span(self):
        today = frappe.utils.today()

        # Create entry 1: 08:00 to 09:30 (does not span lunch)
        entry1 = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "sales_order": self.test_so1,
                "scheduled_date": today,
                "scheduled_time": "08:00:00",
                "estimated_duration": 90,
                "service_bay": self.bay1,
                "status": "Scheduled",
            }
        ).insert(ignore_permissions=True)

        # Create entry 2: 11:00 to 13:00 (spans lunch 12:00-12:30)
        entry2 = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "sales_order": self.test_so2,
                "scheduled_date": today,
                "scheduled_time": "11:00:00",
                "estimated_duration": 120,
                "service_bay": self.bay1,
                "status": "In Progress",
            }
        ).insert(ignore_permissions=True)

        events = get_calendar_events(start=today, end=today)

        # Filter events for our created records
        event_map = {e["name"]: e for e in events if e["name"] in [entry1.name, entry2.name]}

        self.assertIn(entry1.name, event_map)
        self.assertIn(entry2.name, event_map)

        e1 = event_map[entry1.name]
        self.assertFalse(e1["spans_lunch"])
        diag_color = frappe.db.get_value("Schedule Entry Type", "Diagnostic", "color")
        expected_e1_color = diag_color or STATUS_COLOR_MAP["Scheduled"]
        self.assertEqual(e1["color"], expected_e1_color)
        self.assertEqual(e1["end"], f"{today} 09:30:00")

        e2 = event_map[entry2.name]
        self.assertTrue(e2["spans_lunch"])
        expected_e2_color = diag_color or STATUS_COLOR_MAP["In Progress"]
        self.assertEqual(e2["color"], expected_e2_color)
        # 11:00 + 120 min + 30 min lunch = 13:30
        self.assertEqual(e2["end"], f"{today} 13:30:00")

    def test_get_calendar_events_date_filtering(self):
        today = frappe.utils.today()
        tomorrow = str(frappe.utils.add_days(today, 1))

        entry1 = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "sales_order": self.test_so1,
                "scheduled_date": today,
                "scheduled_time": "09:00:00",
                "estimated_duration": 60,
                "service_bay": self.bay1,
                "status": "Scheduled",
            }
        ).insert(ignore_permissions=True)

        events_today = get_calendar_events(start=today, end=today)
        events_tomorrow = get_calendar_events(start=tomorrow, end=tomorrow)

        today_names = [e["name"] for e in events_today]
        tomorrow_names = [e["name"] for e in events_tomorrow]

        self.assertIn(entry1.name, today_names)
        self.assertNotIn(entry1.name, tomorrow_names)

    def test_get_calendar_events_filters_formats(self):
        today = frappe.utils.today()

        entry1 = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "sales_order": self.test_so1,
                "scheduled_date": today,
                "scheduled_time": "09:00:00",
                "estimated_duration": 60,
                "service_bay": self.bay1,
                "status": "Scheduled",
            }
        ).insert(ignore_permissions=True)

        # Test string JSON empty list "[]"
        events1 = get_calendar_events(start=today, end=today, filters="[]")
        self.assertIn(entry1.name, [e["name"] for e in events1])

        # Test string JSON filter list "[[\"Schedule Entry\", \"status\", \"=\", \"Scheduled\"]]"
        events2 = get_calendar_events(
            start=today,
            end=today,
            filters='[["Schedule Entry", "status", "=", "Scheduled"]]',
        )
        self.assertIn(entry1.name, [e["name"] for e in events2])

    def test_resolve_vehicle_info_with_model_formatting(self):
        today = frappe.utils.today()
        # Create a test Repair Vehicle with Model and Year
        vin = f"TESTVIN{frappe.generate_hash(length=8)}"
        vehicle = frappe.get_doc(
            {
                "doctype": "Repair Vehicle",
                "vin": vin,
            }
        ).insert(ignore_permissions=True)

        frappe.db.set_value(
            "Repair Vehicle",
            vehicle.name,
            {
                "model_year": "2023",
                "manufacturer": "Tesla",
                "model": "Model Y",
                "trim": "Long Range",
            },
        )

        # Create Project linked to vehicle
        project = frappe.get_doc(
            {
                "doctype": "Project",
                "project_name": f"Project {vin}",
                "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
                "custom_repair_vehicle": vehicle.name,
                "sales_order": self.test_so1,
            }
        ).insert(ignore_permissions=True)

        entry = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "sales_order": self.test_so1,
                "project": project.name,
                "scheduled_date": today,
                "scheduled_time": "10:00:00",
                "estimated_duration": 60,
                "service_bay": self.bay1,
                "status": "Scheduled",
            }
        ).insert(ignore_permissions=True)

        events = get_calendar_events(start=today, end=today)
        event_dict = next((e for e in events if e["name"] == entry.name), None)

        self.assertIsNotNone(event_dict)
        self.assertIn("2023 Model Y Long Range", event_dict["repair_vehicle"])
        self.assertIn("2023 Model Y Long Range", event_dict["title"])

    def test_get_calendar_events_provisional_fields_and_entry_type(self):
        today = frappe.utils.today()
        entry = frappe.get_doc(
            {
                "doctype": "Schedule Entry",
                "entry_type": "Diagnostic",
                "provisional_customer_name": "Jane Quick",
                "provisional_vehicle_info": "2022 Model 3",
                "scheduled_date": today,
                "scheduled_time": "14:00:00",
                "estimated_duration": 45,
                "service_bay": self.bay1,
                "status": "Scheduled",
            }
        ).insert(ignore_permissions=True)

        events = get_calendar_events(start=today, end=today)
        event_dict = next((e for e in events if e["name"] == entry.name), None)

        self.assertIsNotNone(event_dict)
        self.assertEqual(event_dict["customer"], "Jane Quick")
        self.assertEqual(event_dict["repair_vehicle"], "2022 Model 3")
        self.assertIn("Jane Quick", event_dict["title"])
        self.assertIn("2022 Model 3", event_dict["title"])
        self.assertEqual(event_dict["entry_type"], "Diagnostic")
        if frappe.db.exists("Schedule Entry Type", "Diagnostic"):
            diag_color = frappe.db.get_value("Schedule Entry Type", "Diagnostic", "color")
            if diag_color:
                self.assertEqual(event_dict["color"], diag_color)



