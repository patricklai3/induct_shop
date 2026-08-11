# Copyright (c) 2026, Induct and contributors
# For license information, please see license.txt

import unittest
import frappe
from induct_shop.tests import test_fixtures


class TestQuotationApprovalRecord(unittest.TestCase):
	def setUp(self):
		test_fixtures.setup_all()

	def tearDown(self):
		test_fixtures.teardown_transactional()

	def test_quotation_approval_record_doctype_schema(self):
		"""Verify Quotation Approval Record DocType existence and submittability."""
		self.assertTrue(frappe.db.exists("DocType", "Quotation Approval Record"))
		doc = frappe.get_doc("DocType", "Quotation Approval Record")
		self.assertEqual(doc.is_submittable, 1)

	def test_quotation_approval_item_doctype_schema(self):
		"""Verify Quotation Approval Item child table DocType existence."""
		self.assertTrue(frappe.db.exists("DocType", "Quotation Approval Item"))
		doc = frappe.get_doc("DocType", "Quotation Approval Item")
		self.assertEqual(doc.istable, 1)

	def test_quotation_custom_fields_exist(self):
		"""Verify custom fields added to Quotation for quotation approval."""
		meta = frappe.get_meta("Quotation")

		fields_to_check = [
			("approval_token", "Data", 1),
			("approval_token_status", "Select", 1),
			("approval_token_expiry", "Datetime", 1),
			("approval_link_sent_via", "Select", 1),
			("approval_reminder_sent", "Check", 1),
			("approval_resend_count", "Int", 1),
		]

		for fieldname, fieldtype, allow_on_submit in fields_to_check:
			self.assertTrue(
				meta.has_field(fieldname),
				f"Quotation metadata missing custom field: {fieldname}"
			)
			field = meta.get_field(fieldname)
			self.assertEqual(
				field.fieldtype,
				fieldtype,
				f"Field {fieldname} fieldtype mismatch"
			)
			self.assertEqual(
				field.allow_on_submit,
				allow_on_submit,
				f"Field {fieldname} allow_on_submit mismatch"
			)

	def test_shop_settings_approval_fields_exist(self):
		"""Verify approval configuration fields exist on Shop Settings single DocType."""
		meta = frappe.get_meta("Shop Settings")

		expected_fields = [
			"approval_token_expiry_hours",
			"approval_reminder_hours_before",
			"max_approval_resends",
			"quotation_approval_print_format",
		]

		for fieldname in expected_fields:
			self.assertTrue(
				meta.has_field(fieldname),
				f"Shop Settings missing field: {fieldname}"
			)

		settings = frappe.get_single("Shop Settings")
		self.assertEqual(settings.approval_token_expiry_hours, 72)
		self.assertEqual(settings.approval_reminder_hours_before, 24)
		self.assertEqual(settings.max_approval_resends, 3)
		self.assertEqual(settings.get("quotation_approval_print_format") or "Standard", "Standard")
