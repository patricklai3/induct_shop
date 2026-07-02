# Copyright (c) 2026, Induct and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleCheckin(Document):
	def after_insert(self):
		self.create_project()

	def create_project(self):
		if not self.project:
			project_name = f"{self.customer} - {self.vehicle}"
			project = frappe.get_doc({
				"doctype": "Project",
				"project_name": project_name,
				"status": "Open",
				"customer": self.customer,
				"custom_repair_vehicle": self.vehicle
			})
			project.insert(ignore_permissions=True)
			self.db_set("project", project.name)
