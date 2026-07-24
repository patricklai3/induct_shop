import unittest
import frappe


class TestServiceBay(unittest.TestCase):
	def setUp(self):
		# Ensure Equipment Tag 'Lift' exists for testing child table
		if not frappe.db.exists("Equipment Tag", "Test Lift"):
			doc = frappe.get_doc({
				"doctype": "Equipment Tag",
				"tag_name": "Test Lift",
				"description": "Test Automotive lift"
			})
			doc.insert(ignore_permissions=True)

	def tearDown(self):
		if frappe.db.exists("Service Bay", "Test Bay Alpha"):
			frappe.delete_doc("Service Bay", "Test Bay Alpha", force=True, ignore_permissions=True)
		if frappe.db.exists("Service Bay", "Test Bay Beta"):
			frappe.delete_doc("Service Bay", "Test Bay Beta", force=True, ignore_permissions=True)
		if frappe.db.exists("Equipment Tag", "Test Lift"):
			frappe.delete_doc("Equipment Tag", "Test Lift", force=True, ignore_permissions=True)

	def test_service_bay_creation_and_equipment(self):
		bay = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": "Test Bay Alpha",
			"is_active": 1,
			"description": "Primary test bay with lift",
			"equipment": [
				{"equipment_tag": "Test Lift"}
			]
		})
		bay.insert(ignore_permissions=True)

		self.assertTrue(frappe.db.exists("Service Bay", "Test Bay Alpha"))
		saved_bay = frappe.get_doc("Service Bay", "Test Bay Alpha")
		self.assertEqual(len(saved_bay.equipment), 1)
		self.assertEqual(saved_bay.equipment[0].equipment_tag, "Test Lift")

	def test_service_bay_active_filtering(self):
		bay_active = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": "Test Bay Alpha",
			"is_active": 1
		}).insert(ignore_permissions=True)

		bay_inactive = frappe.get_doc({
			"doctype": "Service Bay",
			"bay_name": "Test Bay Beta",
			"is_active": 0
		}).insert(ignore_permissions=True)

		active_bays = frappe.get_all("Service Bay", filters={"is_active": 1}, pluck="name")
		self.assertIn("Test Bay Alpha", active_bays)
		self.assertNotIn("Test Bay Beta", active_bays)


if __name__ == "__main__":
	unittest.main()
