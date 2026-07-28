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
from induct_shop.tests.test_fixtures import setup_all, teardown_transactional, create_test_sales_order, PREFIX


class TestSchedulingApi(unittest.TestCase):
    def setUp(self):
        self.emp_map = setup_all()

        # Define bay constant aliases
        self.bay1 = f"{PREFIX}Bay 1"
        self.bay2 = f"{PREFIX}Bay 2"

        # Create transactional Sales Orders on demand
        self.test_so1 = create_test_sales_order(f"{PREFIX}SO-SCHED-01")
        self.test_so2 = create_test_sales_order(f"{PREFIX}SO-SCHED-02")
        self.test_so3 = create_test_sales_order(f"{PREFIX}SO-SCHED-03")

    def tearDown(self):
        teardown_transactional(self.emp_map.values())

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
            "service_bay": self.bay1,
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Check 10:00 to 12:00 -> should be available
        avail = check_bay_availability(self.bay1, date, "10:00:00", 120)
        self.assertTrue(avail)

        # Check different bay at 08:00 -> should be available
        avail_bay2 = check_bay_availability(self.bay2, date, "08:00:00", 120)
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
            "service_bay": self.bay1,
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Overlapping attempt: 09:00 to 11:00
        avail = check_bay_availability(self.bay1, date, "09:00:00", 120)
        self.assertFalse(avail)

        # Schedule Entry controller should throw ValidationError on insert
        se2 = frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so2,
            "scheduled_date": date,
            "scheduled_time": "09:00:00",
            "estimated_duration": 120,
            "service_bay": self.bay1,
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
            "service_bay": self.bay1,
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Excluding self should show bay as available
        avail = check_bay_availability(self.bay1, date, "08:00:00", 120, exclude_entry=se.name)
        self.assertTrue(avail)

        # Updating the entry to same slot should succeed without self-conflict error
        se.notes = "Updated notes"
        se.save(ignore_permissions=True)

    # --- 3. Auto-Assign Bay Tests ---
    def test_auto_assign_bay(self):
        date = frappe.utils.today()
        # Bay 1 and Bay 2 are free. Both have "Lift".
        assigned = auto_assign_bay(date, "08:00:00", 60, required_tags=["Lift"])
        self.assertIn(assigned, [self.bay1, self.bay2])

        # Require "Alignment Rack" -> only Bay 2 has it
        assigned_align = auto_assign_bay(date, "08:00:00", 60, required_tags=["Alignment Rack"])
        self.assertEqual(assigned_align, self.bay2)

    def test_auto_assign_bay_no_capacity_raises(self):
        date = frappe.utils.today()

        # Book Bay 2 (which is the only bay with "Alignment Rack")
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": self.bay2,
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Attempt to auto assign at 08:30 requiring "Alignment Rack" -> Bay 2 is occupied
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

        # Book Bay 1 at 08:00:00 for 120 min
        frappe.get_doc({
            "doctype": "Schedule Entry",
            "sales_order": self.test_so1,
            "scheduled_date": date,
            "scheduled_time": "08:00:00",
            "estimated_duration": 120,
            "service_bay": self.bay1,
            "status": "Scheduled"
        }).insert(ignore_permissions=True)

        # Check slots specific to Bay 1
        bay1_slots = get_available_slots(date, 60, service_bay=self.bay1)
        bay1_times = [s["start_time"] for s in bay1_slots]
        self.assertNotIn("08:00", bay1_times)
        self.assertNotIn("08:30", bay1_times)
        self.assertNotIn("09:00", bay1_times)
        self.assertNotIn("09:30", bay1_times)
        self.assertIn("10:00", bay1_times)

    # --- 5. Equipment Tag & Holiday API Tests ---
    def test_get_required_equipment_tags(self):
        from induct_shop.api.scheduling import get_required_equipment_tags
        tags = get_required_equipment_tags(self.test_so1)
        self.assertIsInstance(tags, list)

    def test_is_holiday(self):
        from induct_shop.api.scheduling import is_holiday
        res = is_holiday(frappe.utils.today())
        self.assertIn("is_holiday", res)
        self.assertIn("description", res)


if __name__ == "__main__":
    unittest.main()
