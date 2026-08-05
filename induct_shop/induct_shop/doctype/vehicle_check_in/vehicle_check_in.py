# Copyright (c) 2026, Induct and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleCheckin(Document):
	def after_insert(self):
		self.create_project()
		self.update_originating_schedule_entry()

	def update_originating_schedule_entry(self):
		if self.schedule_entry and frappe.db.exists("Schedule Entry", self.schedule_entry):
			update_dict = {}
			if self.project:
				update_dict["project"] = self.project
			if self.vehicle:
				update_dict["repair_vehicle"] = self.vehicle
			if self.customer:
				update_dict["customer"] = self.customer
			update_dict["vehicle_check_in"] = self.name

			frappe.db.set_value("Schedule Entry", self.schedule_entry, update_dict)

	def create_project(self):
		if not self.project:
			vehicle_desc = self.get_vehicle_description()
			base_project_name = f"{self.customer} - {vehicle_desc} - {self.name}" if vehicle_desc else f"{self.customer} - {self.name}"
			project_name = base_project_name
			counter = 1
			while frappe.db.exists("Project", {"project_name": project_name}):
				counter += 1
				project_name = f"{base_project_name} ({counter})"

			project = frappe.get_doc({
				"doctype": "Project",
				"project_name": project_name,
				"status": "Open",
				"customer": self.customer,
				"custom_repair_vehicle": self.vehicle
			})
			project.insert(ignore_permissions=True)
			self.db_set("project", project.name)

	def get_vehicle_description(self):
		if not self.vehicle:
			return ""
		v_details = frappe.db.get_value(
			"Repair Vehicle",
			self.vehicle,
			["model", "trim"],
			as_dict=True
		)
		if v_details:
			parts = []
			for field in ("model", "trim"):
				val = (v_details.get(field) or "").strip()
				if val and val not in parts:
					parts.append(val)
			if parts:
				return " ".join(parts)
		return self.vehicle


