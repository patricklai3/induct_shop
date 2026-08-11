import unittest
import frappe
from frappe.utils import flt
from induct_shop.tests import test_fixtures
from induct_shop.api.quotation_approval import compute_requires_manager_approval, handle_quotation_cancel

class TestQuotationApprovalStage2(unittest.TestCase):
    def setUp(self):
        test_fixtures.setup_all()

    def tearDown(self):
        test_fixtures.teardown_transactional()

    def _create_test_quotation(self, grand_total=100.0, discount_pct=0.0):
        """Helper to create a draft Quotation document for testing."""
        quotation = frappe.get_doc({
            "doctype": "Quotation",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            "party_name": test_fixtures.CUSTOMER,
            "quotation_to": "Customer",
            "currency": "USD",
            "selling_price_list": "Standard Selling",
            "items": [{
                "item_code": f"{test_fixtures.PREFIX}SERVICE_001",
                "qty": 1,
                "price_list_rate": grand_total,
                "rate": grand_total * (1 - (discount_pct / 100.0)),
                "discount_percentage": discount_pct
            }]
        })
        return quotation

    def test_requires_manager_approval_amount_threshold(self):
        """Test that requires_manager_approval flag evaluates grand_total against Shop Settings threshold."""
        settings = frappe.get_single("Shop Settings")
        orig_amount = settings.approval_threshold_amount
        orig_discount = settings.approval_threshold_discount_pct

        try:
            settings.approval_threshold_amount = 500.0
            settings.approval_threshold_discount_pct = 100.0  # Disable discount check
            settings.save(ignore_permissions=True)

            # Below threshold: auto-pass (requires_manager_approval = 0)
            q1 = self._create_test_quotation(grand_total=300.0, discount_pct=0.0)
            q1.insert(ignore_permissions=True)
            self.assertEqual(q1.requires_manager_approval, 0)

            # Above threshold: requires review (requires_manager_approval = 1)
            q2 = self._create_test_quotation(grand_total=600.0, discount_pct=0.0)
            q2.insert(ignore_permissions=True)
            self.assertEqual(q2.requires_manager_approval, 1)

        finally:
            settings.approval_threshold_amount = orig_amount
            settings.approval_threshold_discount_pct = orig_discount
            settings.save(ignore_permissions=True)

    def test_requires_manager_approval_discount_threshold(self):
        """Test that requires_manager_approval flag evaluates item discount against Shop Settings threshold."""
        settings = frappe.get_single("Shop Settings")
        orig_amount = settings.approval_threshold_amount
        orig_discount = settings.approval_threshold_discount_pct

        try:
            settings.approval_threshold_amount = 1000.0  # High amount threshold
            settings.approval_threshold_discount_pct = 10.0  # 10% max discount
            settings.save(ignore_permissions=True)

            # Discount below threshold (5% <= 10%)
            q1 = self._create_test_quotation(grand_total=300.0, discount_pct=5.0)
            q1.insert(ignore_permissions=True)
            self.assertEqual(q1.requires_manager_approval, 0)

            # Discount above threshold (15% > 10%)
            q2 = self._create_test_quotation(grand_total=300.0, discount_pct=15.0)
            q2.insert(ignore_permissions=True)
            self.assertEqual(q2.requires_manager_approval, 1)

        finally:
            settings.approval_threshold_amount = orig_amount
            settings.approval_threshold_discount_pct = orig_discount
            settings.save(ignore_permissions=True)

    def test_workflow_exists_and_active(self):
        """Test that Quotation Approval Workflow fixture is installed and active."""
        self.assertTrue(frappe.db.exists("Workflow", {"document_type": "Quotation", "is_active": 1}))
        wf = frappe.get_doc("Workflow", {"document_type": "Quotation"})
        self.assertEqual(wf.is_active, 1)
        self.assertEqual(wf.workflow_state_field, "workflow_state")
        state_names = [s.state for s in wf.states]
        expected_states = [
            "Draft", "Pending Manager Approval", "Internally Approved",
            "Sent to Customer", "Customer Approved", "Partially Approved",
            "Customer Rejected", "Customer No Response", "Cancelled"
        ]
        for st in expected_states:
            self.assertIn(st, state_names)

    def test_on_cancel_invalidates_token(self):
        """Test that cancelling a quotation with active token sets approval_token_status = Expired."""
        q = self._create_test_quotation(grand_total=100.0)
        q.insert(ignore_permissions=True)
        q.approval_token = "test_token_12345"
        q.approval_token_status = "Active"
        q.submit()

        handle_quotation_cancel(q)
        q.reload()
        self.assertEqual(q.approval_token_status, "Expired")
