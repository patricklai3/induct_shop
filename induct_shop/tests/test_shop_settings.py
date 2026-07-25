import unittest
import frappe
from induct_shop.tests.test_fixtures import setup_all


class TestShopSettings(unittest.TestCase):
	def setUp(self):
		setup_all()

	def test_shop_settings_defaults(self):
		settings = frappe.get_single("Shop Settings")
		self.assertIsNotNone(settings)
		self.assertEqual(str(settings.operating_hours_start), "08:00:00")
		self.assertEqual(str(settings.operating_hours_end), "17:00:00")
		self.assertEqual(str(settings.break_start), "12:00:00")
		self.assertEqual(str(settings.break_end), "12:30:00")
		self.assertEqual(settings.default_slot_interval, 30)
		self.assertIn(settings.scheduling_horizon_days, (15, 30))
		self.assertEqual(settings.technician_designation, "Technician")
		self.assertEqual(settings.enable_technician_capacity, 1)

	def test_shop_settings_update(self):
		settings = frappe.get_single("Shop Settings")
		original_interval = settings.default_slot_interval
		try:
			settings.default_slot_interval = 45
			settings.save(ignore_permissions=True)

			updated = frappe.get_single("Shop Settings")
			self.assertEqual(updated.default_slot_interval, 45)
		finally:
			settings.default_slot_interval = original_interval
			settings.save(ignore_permissions=True)


if __name__ == "__main__":
	unittest.main()
