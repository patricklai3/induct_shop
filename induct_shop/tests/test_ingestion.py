import unittest
from unittest.mock import patch, MagicMock
import frappe
from induct_shop.tests import test_fixtures
from induct_shop.api.service_parts_selector import ingest_part, ingest_service

TEST_PARTS = """1083401-05-O	INSTRUMENT PANEL - SUBASSEMBLY		Model 3 Jun 2017 - Dec 2023	14 - INSTRUMENT PANEL	1405 - Instrument Panel	Dash Panel
1083401-05-O	INSTRUMENT PANEL - SUBASSEMBLY		Model Y Jan 2020 - Jan 2025	14 - INSTRUMENT PANEL	1405 - Instrument Panel	Dash Panel
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model Y Jan 2020 - Jan 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model 3 Jun 2017 - Dec 2023	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188354-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - LEFT HAND	FR LWR COMP LINK ASSY, CN, LH	Model 3 Jan 2024	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188354-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - LEFT HAND	FR LWR COMP LINK ASSY, CN, LH	Model Y Feb 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model Y Feb 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model 3 Jan 2024	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
"""

SERVICE_URL = "https://service.tesla.com/docs/Model3/ServiceManual/en-us/GUID-DE61971B-D5F1-4C5C-9050-DE313445276D.html"

TEST_ITEM_CODES = ["1083401", "2188359", "2188354", "31010202"]

class TestIngestion(unittest.TestCase):
    def setUp(self):
        test_fixtures.setup_all()
        self._cleanup_test_items()

    def tearDown(self):
        self._cleanup_test_items()
        test_fixtures.teardown_transactional()

    def _cleanup_test_items(self):
        for code in TEST_ITEM_CODES:
            # Delete variants first if any
            variants = frappe.get_all("Item", filters={"variant_of": code}, fields=["name"])
            for v in variants:
                frappe.delete_doc("Item", v.name, force=1, ignore_permissions=True)
            if frappe.db.exists("Item", code):
                frappe.delete_doc("Item", code, force=1, ignore_permissions=True)
        frappe.db.commit()

    def test_ingest_part(self):
        results = ingest_part(TEST_PARTS)
        self.assertTrue(len(results) > 0)

        # Check expected base items created (first 7 digits)
        self.assertTrue(frappe.db.exists("Item", "1083401"))
        self.assertTrue(frappe.db.exists("Item", "2188359"))
        self.assertTrue(frappe.db.exists("Item", "2188354"))

        # Check expected variants created
        self.assertTrue(frappe.db.exists("Item", "1083401-05-O-OEM-NEW"))
        self.assertTrue(frappe.db.exists("Item", "2188359-10-B-OEM-NEW"))
        self.assertTrue(frappe.db.exists("Item", "2188354-10-B-OEM-NEW"))

        # Verify deduplication for Item 1083401 (Instrument Panel)
        item = frappe.get_doc("Item", "1083401")
        models = [d.model for d in item.custom_model_compatibility]
        self.assertEqual(len(models), 2)
        self.assertIn("Model 3", models)
        self.assertIn("Model Y", models)

    @patch("induct_shop.api.service_parts_selector.extract_mobile_capability", return_value=True)
    @patch("requests.get")
    def test_ingest_service(self, mock_get, mock_mobile):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""
        <html>
        <head>
            <title>Front Lower Compliance Link - Right Hand (Remove and Replace)</title>
            <meta name="description" content="Correction code 31010202 FRT 0.5 NOTE: Replace compliance link.">
        </head>
        <body></body>
        </html>
        """
        mock_get.return_value = mock_response

        res = ingest_service(SERVICE_URL)

        self.assertEqual(res["item_code"], "31010202")
        self.assertEqual(res["frt_value"], 0.5)
        self.assertTrue(frappe.db.exists("Item", "31010202"))

        item = frappe.get_doc("Item", "31010202")
        self.assertEqual(item.custom_frt, 0.5)
        self.assertEqual(item.is_stock_item, 0)
