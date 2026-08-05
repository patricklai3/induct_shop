import unittest
import frappe
from induct_shop.tests import test_fixtures


class TestScheduleEntryType(unittest.TestCase):
    def setUp(self):
        test_fixtures.setup_all()

    def test_seed_schedule_entry_types_exist(self):
        """Verify all 5 standard seed entry types exist with expected attributes."""
        expected_types = {
            "Diagnostic": {"requires_sales_order": 0, "color": "#1f538d"},
            "Repair": {"requires_sales_order": 1, "color": "#2e7d32"},
            "Meeting": {"requires_sales_order": 0, "color": "#7b1fa2"},
            "Maintenance / Shop Cleaning": {"requires_sales_order": 0, "color": "#c62828"},
            "Internal Service": {"requires_sales_order": 0, "color": "#ef6c00"},
        }

        for type_name, attrs in expected_types.items():
            self.assertTrue(
                frappe.db.exists("Schedule Entry Type", type_name),
                f"Schedule Entry Type '{type_name}' should exist in DB",
            )
            doc = frappe.get_doc("Schedule Entry Type", type_name)
            self.assertEqual(
                doc.requires_sales_order,
                attrs["requires_sales_order"],
                f"'{type_name}' requires_sales_order mismatch",
            )
            self.assertEqual(
                doc.color,
                attrs["color"],
                f"'{type_name}' color mismatch",
            )

    def test_create_custom_schedule_entry_type(self):
        """Verify custom Schedule Entry Type creation and uniqueness rule."""
        type_name = "_IST_Custom_Type"
        if frappe.db.exists("Schedule Entry Type", type_name):
            frappe.delete_doc("Schedule Entry Type", type_name, force=1)

        doc = frappe.get_doc({
            "doctype": "Schedule Entry Type",
            "type_name": type_name,
            "requires_sales_order": 0,
            "color": "#123456",
            "description": "Test custom schedule entry type"
        })
        doc.insert()

        self.assertTrue(frappe.db.exists("Schedule Entry Type", type_name))
        fetched = frappe.get_doc("Schedule Entry Type", type_name)
        self.assertEqual(fetched.color, "#123456")

        # Cleanup
        frappe.delete_doc("Schedule Entry Type", type_name, force=1)
