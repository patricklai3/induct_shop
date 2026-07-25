import unittest
import frappe
from induct_shop.tests.test_fixtures import setup_all, PREFIX


class TestServiceBay(unittest.TestCase):
	def setUp(self):
		setup_all()
		self.bay_alpha = f"{PREFIX}Test Bay Alpha"
		self.bay_beta = f"{PREFIX}Test Bay Beta"

	def tearDown(self):
		if frappe.db.exists("Service Bay", self.bay_alpha):
			frappe.delete_doc("Service Bay", self.bay_alpha, force=True, ignore_permissions=True)
		if frappe.db.exists("Service Bay", self.bay_beta):
			frappe.delete_doc("Service Bay", self.bay_beta, force=True, ignore_permissions=True)

	def test_service_bay_creation_and_equipment(self):
		bay = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": self.bay_alpha,
			"is_active": 1,
			"description": "Primary test bay with lift",
			"equipment": [
				{"equipment_tag": "Lift"}
			]
		})
		bay.insert(ignore_permissions=True)

		self.assertTrue(frappe.db.exists("Service Bay", self.bay_alpha))
		saved_bay = frappe.get_doc("Service Bay", self.bay_alpha)
		self.assertEqual(len(saved_bay.equipment), 1)
		self.assertEqual(saved_bay.equipment[0].equipment_tag, "Lift")

	def test_service_bay_active_filtering(self):
		bay_active = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": self.bay_alpha,
			"is_active": 1
		}).insert(ignore_permissions=True)

		bay_inactive = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": self.bay_beta,
			"is_active": 0
		}).insert(ignore_permissions=True)

		active_bays = frappe.get_all("Service Bay", filters={"is_active": 1}, pluck="name")
		self.assertIn(self.bay_alpha, active_bays)
		self.assertNotIn(self.bay_beta, active_bays)


if __name__ == "__main__":
	unittest.main()
