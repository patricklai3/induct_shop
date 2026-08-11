import frappe
from frappe.utils import flt

def compute_requires_manager_approval(doc, method=None):
    """
    Evaluates Shop Settings threshold amount and discount percentage to set
    requires_manager_approval = 1 or 0 when a Draft Quotation is saved (docstatus == 0).
    """
    if doc.docstatus != 0:
        return

    threshold_amount = flt(frappe.db.get_single_value("Shop Settings", "approval_threshold_amount"))
    threshold_discount_pct = flt(frappe.db.get_single_value("Shop Settings", "approval_threshold_discount_pct"))

    # Determine maximum discount percentage across all line items
    max_discount_pct = 0.0
    for item in (doc.items or []):
        item_disc = flt(item.get("discount_percentage", 0))
        if not item_disc and flt(item.get("price_list_rate")) > 0 and flt(item.get("discount_amount")) > 0:
            item_disc = (flt(item.discount_amount) / flt(item.price_list_rate)) * 100.0
        if item_disc > max_discount_pct:
            max_discount_pct = item_disc

    # Evaluate amount threshold
    # If threshold_amount > 0: amount > threshold_amount requires manager approval
    # If threshold_amount == 0: any amount > 0 requires manager approval
    if threshold_amount > 0:
        amount_exceeds = (flt(doc.grand_total) > threshold_amount)
    else:
        amount_exceeds = (flt(doc.grand_total) > 0)

    # Evaluate discount threshold
    # If threshold_discount_pct == 100: discount check is disabled
    # Otherwise: max_discount_pct > threshold_discount_pct requires manager approval
    if threshold_discount_pct >= 100:
        discount_exceeds = False
    else:
        discount_exceeds = (max_discount_pct > threshold_discount_pct)

    if amount_exceeds or discount_exceeds:
        doc.requires_manager_approval = 1
    else:
        doc.requires_manager_approval = 0

def handle_quotation_cancel(doc, method=None):
    """
    On Quotation cancellation (docstatus == 2), invalidate any active customer approval link token.
    """
    if doc.get("approval_token_status") == "Active":
        frappe.db.set_value(
            "Quotation",
            doc.name,
            "approval_token_status",
            "Expired",
            update_modified=False
        )
        doc.approval_token_status = "Expired"
