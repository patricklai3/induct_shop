import unittest
import frappe


class IntegrationTestVehicleCheckin(unittest.TestCase):
	"""
	Integration tests for VehicleCheckin project auto-creation and naming.
	"""

	@classmethod
	def setUpClass(cls):
		cls.setup_test_data()


	@classmethod
	def setup_test_data(cls):
		# 1. Ensure test Customer exists
		if not frappe.db.exists("Customer", "_Test Checkin Customer"):
			frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "_Test Checkin Customer",
				"customer_group": "Individual",
				"territory": "All Territories"
			}).insert(ignore_permissions=True)

		# 2. Ensure test Repair Vehicle exists with Make, Model, Trim
		vin = "TEST-VIN-VCI-01"
		if not frappe.db.exists("Repair Vehicle", vin):
			frappe.get_doc({
				"doctype": "Repair Vehicle",
				"vin": vin,
				"customer": "_Test Checkin Customer"
			}).insert(ignore_permissions=True)

		frappe.db.set_value("Repair Vehicle", vin, {
			"manufacturer": "Tesla",
			"model": "Model S",
			"trim": "Plaid"
		})



	def test_vehicle_checkin_project_creation_naming(self):
		vci = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": "_Test Checkin Customer",
			"vehicle": "TEST-VIN-VCI-01",
			"intake_mileage": 15000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		self.assertTrue(vci.project)
		project = frappe.get_doc("Project", vci.project)
		expected_project_name = f"_Test Checkin Customer - Tesla Model S Plaid - {vci.name}"
		self.assertEqual(project.project_name, expected_project_name)
		self.assertEqual(project.customer, "_Test Checkin Customer")
		self.assertEqual(project.custom_repair_vehicle, "TEST-VIN-VCI-01")

	def test_duplicate_vehicle_checkin_same_customer_car(self):
		vci1 = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": "_Test Checkin Customer",
			"vehicle": "TEST-VIN-VCI-01",
			"intake_mileage": 16000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		# Submit/Insert second check-in for the same customer & vehicle
		vci2 = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": "_Test Checkin Customer",
			"vehicle": "TEST-VIN-VCI-01",
			"intake_mileage": 17000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		self.assertTrue(vci1.project)
		self.assertTrue(vci2.project)
		self.assertNotEqual(vci1.project, vci2.project)

		project1 = frappe.get_doc("Project", vci1.project)
		project2 = frappe.get_doc("Project", vci2.project)

		self.assertEqual(project1.project_name, f"_Test Checkin Customer - Tesla Model S Plaid - {vci1.name}")
		self.assertEqual(project2.project_name, f"_Test Checkin Customer - Tesla Model S Plaid - {vci2.name}")


def run_tests():
	import unittest
	suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestVehicleCheckin)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	if not result.wasSuccessful():
		raise Exception("Vehicle Check-in unit tests failed!")
	return {"status": "success", "tests_run": result.testsRun}



