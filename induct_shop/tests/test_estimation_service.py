import unittest
from unittest.mock import patch
import frappe

from induct_shop.api.estimation_service import (
    get_estimate,
    get_total_estimate,
    _get_frt
)
from induct_shop.scheduling.estimation_light import estimate_duration


class TestEstimationService(unittest.TestCase):
    def setUp(self):
        # Ensure 'Brake' Item Group exists
        if not frappe.db.exists("Item Group", "Brake"):
            ig = frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": "Brake",
                "parent_item_group": "All Item Groups"
            })
            ig.insert(ignore_permissions=True)

        # Create test items with custom_frt in hours (1.0 hr = 60 mins, 1.5 hr = 90 mins)
        if not frappe.db.exists("Item", "EST_TEST_ITEM_001"):
            item1 = frappe.get_doc({
                "doctype": "Item",
                "item_code": "EST_TEST_ITEM_001",
                "item_name": "Test Brake Pad Front",
                "item_group": "Brake",
                "is_stock_item": 0,
                "is_sales_item": 1,
                "stock_uom": "Hour",
                "custom_frt": 1.0
            })
            item1.insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Item", "EST_TEST_ITEM_001", "custom_frt", 1.0)

        if not frappe.db.exists("Item", "EST_TEST_ITEM_002"):
            item2 = frappe.get_doc({
                "doctype": "Item",
                "item_code": "EST_TEST_ITEM_002",
                "item_name": "Test Brake Rotor Rear",
                "item_group": "Brake",
                "is_stock_item": 0,
                "is_sales_item": 1,
                "stock_uom": "Hour",
                "custom_frt": 1.5
            })
            item2.insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Item", "EST_TEST_ITEM_002", "custom_frt", 1.5)

    def test_get_estimate_with_custom_frt(self):
        # Item 1 has custom_frt=60.0 and item_group="Brake" (sigma=0.20)
        # P80 for FRT=60, sigma=0.20: exp(ln(60) + 0.20 * 0.8416) = 70.9985 -> ceil is 71
        est = get_estimate("EST_TEST_ITEM_001")
        expected = estimate_duration(60.0, sigma=0.20)
        self.assertEqual(est, expected)
        self.assertEqual(est, 71)

    def test_get_estimate_override_sigma_and_fallback(self):
        # Override sigma explicitly
        est_custom_sigma = get_estimate("EST_TEST_ITEM_001", sigma=0.30)
        self.assertEqual(est_custom_sigma, 78)

        # Missing item uses fallback (60.0 by default)
        est_missing = get_estimate("NON_EXISTENT_ITEM_999")
        self.assertEqual(est_missing, 78)  # default fallback 60.0 with default sigma 0.30 -> 78

        # Missing item with custom fallback_frt
        est_missing_custom = get_estimate("NON_EXISTENT_ITEM_999", fallback_frt=30.0, sigma=0.30)
        self.assertEqual(est_missing_custom, 39)

    def test_get_total_estimate_multi_item(self):
        # Sum of EST_TEST_ITEM_001 (60 min) and EST_TEST_ITEM_002 (90 min)
        # Both in Brake group (sigma=0.20)
        total_est = get_total_estimate(["EST_TEST_ITEM_001", "EST_TEST_ITEM_002"])
        self.assertTrue(total_est > 0)
        self.assertTrue(total_est < (71 + 107))  # Diversification effect: less than naive sum of individual P80s

    def test_get_total_estimate_json_string(self):
        json_str = '["EST_TEST_ITEM_001", "EST_TEST_ITEM_002"]'
        total_est = get_total_estimate(json_str)
        self.assertTrue(total_est > 0)

    def test_get_total_estimate_skip_missing(self):
        # Including non-existent item without skip_missing -> uses fallback (60m)
        total_with_fallback = get_total_estimate(["EST_TEST_ITEM_001", "NON_EXISTENT_ITEM_999"])

        # Including non-existent item with skip_missing=True -> ignores non-existent item
        total_skip = get_total_estimate(["EST_TEST_ITEM_001", "NON_EXISTENT_ITEM_999"], skip_missing=True)
        single_est = get_estimate("EST_TEST_ITEM_001")

        self.assertEqual(total_skip, single_est)
        self.assertTrue(total_with_fallback > total_skip)

    def test_defensive_has_column_mock(self):
        original_has_column = frappe.db.has_column

        def mock_has_column(doctype, fieldname):
            if doctype == "Item" and fieldname == "custom_frt":
                return False
            return original_has_column(doctype, fieldname)

        with patch.object(frappe.db, "has_column", side_effect=mock_has_column):
            frt = _get_frt("EST_TEST_ITEM_001", fallback=45.0)
            self.assertEqual(frt, 45.0)

            # get_estimate should not crash when column doesn't exist
            # Uses fallback FRT 45.0 with item's group "Brake" (sigma 0.20) -> exp(ln(45)+0.20*0.8416) = 53.25 -> 54
            est = get_estimate("EST_TEST_ITEM_001", fallback_frt=45.0)
            self.assertEqual(est, 54)



if __name__ == "__main__":
    unittest.main()
