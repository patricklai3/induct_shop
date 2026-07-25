import unittest
import frappe
from induct_shop.api.service_parts_selector import (
    get_all_equipment_tags,
    update_service_equipment_requirements,
    search_catalog
)
from induct_shop.tests.test_fixtures import setup_all, PREFIX

class TestEquipmentTags(unittest.TestCase):
    def setUp(self):
        setup_all()
        self.item_code = f"{PREFIX}SERVICE_001"

    def test_get_all_equipment_tags(self):
        tags = get_all_equipment_tags()
        tag_names = [t.tag_name for t in tags]
        self.assertIn("Lift", tag_names)
        self.assertIn("Alignment Rack", tag_names)

    def test_update_service_equipment_requirements(self):
        # Update test service with Lift and Alignment Rack
        res = update_service_equipment_requirements(self.item_code, ["Lift", "Alignment Rack"])
        self.assertEqual(res["item_code"], self.item_code)
        self.assertEqual(res["equipment_requirements"], ["Lift", "Alignment Rack"])
        self.assertFalse(res["is_mobile_capable"])

        # Search catalog and verify response
        search_results = search_catalog(self.item_code)
        matched = next((r for r in search_results if r["item_code"] == self.item_code), None)
        self.assertIsNotNone(matched)
        self.assertCountEqual(matched["equipment_requirements"], ["Lift", "Alignment Rack"])
        self.assertEqual(matched["custom_is_mobile_capable"], 0)

        # Clear requirements and verify derived mobile capability
        res_clear = update_service_equipment_requirements(self.item_code, [])
        self.assertTrue(res_clear["is_mobile_capable"])

        search_results_cleared = search_catalog(self.item_code)
        matched_cleared = next((r for r in search_results_cleared if r["item_code"] == self.item_code), None)
        self.assertEqual(matched_cleared["equipment_requirements"], [])
        self.assertEqual(matched_cleared["custom_is_mobile_capable"], 1)

if __name__ == "__main__":
    unittest.main()
