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

		# 3. Ensure test Service Bay exists
		if not frappe.db.exists("Service Bay", "_Test Checkin Bay"):
			frappe.get_doc({
				"doctype": "Service Bay",
				"bay_name": "_Test Checkin Bay",
				"is_active": 1
			}).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay='_Test Checkin Bay'")
		frappe.db.commit()

	def test_schedule_entry_cross_linking(self):
		se = frappe.get_doc({
			"doctype": "Schedule Entry",
			"entry_type": "Diagnostic",
			"scheduled_date": frappe.utils.today(),
			"scheduled_time": "11:00:00",
			"estimated_duration": 45,
			"service_bay": "_Test Checkin Bay",
			"provisional_customer_name": "Provisional Customer",
			"provisional_vehicle_info": "Provisional Vehicle",
			"status": "Scheduled"
		}).insert(ignore_permissions=True)

		vci = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": "_Test Checkin Customer",
			"vehicle": "TEST-VIN-VCI-01",
			"schedule_entry": se.name,
			"intake_mileage": 18000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		se.reload()
		self.assertEqual(se.project, vci.project)
		self.assertEqual(se.repair_vehicle, vci.vehicle)
		self.assertEqual(se.customer, vci.customer)
		self.assertEqual(se.vehicle_check_in, vci.name)



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
		expected_project_name = f"_Test Checkin Customer - Model S Plaid - {vci.name}"
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

		self.assertEqual(project1.project_name, f"_Test Checkin Customer - Model S Plaid - {vci1.name}")
		self.assertEqual(project2.project_name, f"_Test Checkin Customer - Model S Plaid - {vci2.name}")



def run_tests():
	import unittest
	suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestVehicleCheckin)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	if not result.wasSuccessful():
		raise Exception("Vehicle Check-in unit tests failed!")
	return {"status": "success", "tests_run": result.testsRun}



