import unittest
import frappe
from induct_shop.api.service_parts_selector import (
    get_all_equipment_tags,
    update_service_equipment_requirements,
    search_catalog
)

class TestEquipmentTags(unittest.TestCase):
    def setUp(self):
        # Ensure 'Lift' equipment tag exists
        if not frappe.db.exists("Equipment Tag", "Lift"):
            doc = frappe.get_doc({
                "doctype": "Equipment Tag",
                "tag_name": "Lift",
                "description": "Automotive lift"
            })
            doc.insert(ignore_permissions=True)
            
        if not frappe.db.exists("Equipment Tag", "Alignment Rack"):
            doc = frappe.get_doc({
                "doctype": "Equipment Tag",
                "tag_name": "Alignment Rack",
                "description": "Wheel alignment rack"
            })
            doc.insert(ignore_permissions=True)

        # Create dummy service item for testing
        if not frappe.db.exists("Item", "TEST_SERVICE_001"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST_SERVICE_001",
                "item_name": "Test Brake Service",
                "description": "Test brake service description",
                "item_group": "Services",
                "is_stock_item": 0,
                "is_sales_item": 1,
                "stock_uom": "Hour",
                "custom_frt": 1.5
            })
            item.insert(ignore_permissions=True)

    def test_get_all_equipment_tags(self):
        tags = get_all_equipment_tags()
        tag_names = [t.tag_name for t in tags]
        self.assertIn("Lift", tag_names)
        self.assertIn("Alignment Rack", tag_names)

    def test_update_service_equipment_requirements(self):
        # Update test service with Lift and Alignment Rack
        res = update_service_equipment_requirements("TEST_SERVICE_001", ["Lift", "Alignment Rack"])
        self.assertEqual(res["item_code"], "TEST_SERVICE_001")
        self.assertEqual(res["equipment_requirements"], ["Lift", "Alignment Rack"])
        self.assertFalse(res["is_mobile_capable"])

        # Search catalog and verify response
        search_results = search_catalog("TEST_SERVICE_001")
        matched = next((r for r in search_results if r["item_code"] == "TEST_SERVICE_001"), None)
        self.assertIsNotNone(matched)
        self.assertCountEqual(matched["equipment_requirements"], ["Lift", "Alignment Rack"])
        self.assertEqual(matched["custom_is_mobile_capable"], 0)

        # Clear requirements and verify derived mobile capability
        res_clear = update_service_equipment_requirements("TEST_SERVICE_001", [])
        self.assertTrue(res_clear["is_mobile_capable"])

        search_results_cleared = search_catalog("TEST_SERVICE_001")
        matched_cleared = next((r for r in search_results_cleared if r["item_code"] == "TEST_SERVICE_001"), None)
        self.assertEqual(matched_cleared["equipment_requirements"], [])
        self.assertEqual(matched_cleared["custom_is_mobile_capable"], 1)

if __name__ == "__main__":
    unittest.main()
