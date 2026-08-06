import unittest
import frappe
from induct_shop.tests import test_fixtures


class IntegrationTestVehicleCheckin(unittest.TestCase):
	"""
	Integration tests for VehicleCheckin project auto-creation and naming.
	"""

	def setUp(self):
		test_fixtures.setup_all()

	def tearDown(self):
		test_fixtures.teardown_transactional()

	def test_schedule_entry_cross_linking(self):
		se = frappe.get_doc({
			"doctype": "Schedule Entry",
			"entry_type": "Diagnostic",
			"scheduled_date": frappe.utils.today(),
			"scheduled_time": "11:00:00",
			"estimated_duration": 45,
			"service_bay": f"{test_fixtures.PREFIX}Bay 1",
			"provisional_customer_name": "Provisional Customer",
			"provisional_vehicle_info": "Provisional Vehicle",
			"status": "Scheduled"
		}).insert(ignore_permissions=True)

		vci = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": test_fixtures.CUSTOMER,
			"vehicle": test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"],
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
			"customer": test_fixtures.CUSTOMER,
			"vehicle": test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"],
			"intake_mileage": 15000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		self.assertTrue(vci.project)
		project = frappe.get_doc("Project", vci.project)
		expected_project_name = f"{test_fixtures.CUSTOMER} - Model S Plaid - {vci.name}"
		self.assertEqual(project.project_name, expected_project_name)
		self.assertEqual(project.customer, test_fixtures.CUSTOMER)
		self.assertEqual(project.custom_repair_vehicle, test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"])

	def test_duplicate_vehicle_checkin_same_customer_car(self):
		vci1 = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": test_fixtures.CUSTOMER,
			"vehicle": test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"],
			"intake_mileage": 16000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		# Submit/Insert second check-in for the same customer & vehicle
		vci2 = frappe.get_doc({
			"doctype": "Vehicle Check-in",
			"customer": test_fixtures.CUSTOMER,
			"vehicle": test_fixtures.REPAIR_VEHICLE_MODEL_S["vin"],
			"intake_mileage": 17000,
			"check_in_date": frappe.utils.now_datetime()
		}).insert(ignore_permissions=True)

		self.assertTrue(vci1.project)
		self.assertTrue(vci2.project)
		self.assertNotEqual(vci1.project, vci2.project)

		project1 = frappe.get_doc("Project", vci1.project)
		project2 = frappe.get_doc("Project", vci2.project)

		self.assertEqual(project1.project_name, f"{test_fixtures.CUSTOMER} - Model S Plaid - {vci1.name}")
		self.assertEqual(project2.project_name, f"{test_fixtures.CUSTOMER} - Model S Plaid - {vci2.name}")


def run_tests():
	import unittest
	suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestVehicleCheckin)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	if not result.wasSuccessful():
		raise Exception("Vehicle Check-in unit tests failed!")
	return {"status": "success", "tests_run": result.testsRun}




