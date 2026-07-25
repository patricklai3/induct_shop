"""
Sales Order Amendment Handling for Scheduling System.

When a Sales Order is amended (a new version created via ERPNext Amend flow),
this handler updates the linked Schedule Entry:
  - Re-links the SE to the new (amended) SO
  - Sets status to "Needs Review"
  - Recalculates estimated_duration from the amended SO's items
  - Regenerates items_summary
  - Detects bay overlap if the new duration causes conflicts

Registered in hooks.py under doc_events → Sales Order → on_submit.
"""

import frappe
from frappe import _


def handle_amendment(doc, method=None):
    """
    Called on Sales Order on_submit. Only acts when the SO is an amendment
    (i.e., doc.amended_from is set).

    Finds the Schedule Entry linked to the original SO and updates it to
    point to the amended SO, recalculates duration, and checks for overlaps.
    """
    if not doc.amended_from:
        return

    # Find Schedule Entry linked to the original (cancelled) Sales Order
    se_name = frappe.db.get_value(
        "Schedule Entry",
        {"sales_order": doc.amended_from},
        "name",
    )
    if not se_name:
        return

    se_doc = frappe.get_doc("Schedule Entry", se_name)

    # 1. Re-link to the new amended SO
    se_doc.sales_order = doc.name

    # 2. Set status to "Needs Review"
    se_doc.status = "Needs Review"

    # 3. Recalculate estimated_duration from the amended SO's items
    from induct_shop.api.estimation_service import get_total_estimate

    operations = []
    for item in getattr(doc, "items", []):
        code = getattr(item, "item_code", None)
        if not code:
            continue

        frt_hours = None
        # Priority 1: Line item custom_frt override
        if hasattr(item, "custom_frt") and item.custom_frt:
            try:
                val = float(item.custom_frt)
                if val > 0:
                    frt_hours = val
            except (ValueError, TypeError):
                pass

        # Priority 2: Line item qty when specified in hours or for non-stock items
        if frt_hours is None and hasattr(item, "qty") and item.qty:
            try:
                qty_val = float(item.qty)
                uom = getattr(item, "uom", "") or getattr(item, "stock_uom", "")
                is_hour_uom = str(uom).lower() in ("hour", "hours", "hr", "hrs")
                is_non_stock = False
                if frappe.db.exists("Item", code):
                    is_non_stock = not frappe.db.get_value("Item", code, "is_stock_item")
                if (is_hour_uom or is_non_stock) and qty_val > 0:
                    frt_hours = qty_val
            except (ValueError, TypeError):
                pass

        if frt_hours is not None:
            operations.append({"item_code": code, "flat_rate_hours": frt_hours})
        else:
            operations.append(code)

    old_duration = se_doc.estimated_duration or 0
    if operations:
        se_doc.estimated_duration = get_total_estimate(operations)
    else:
        se_doc.estimated_duration = 0

    # 4. Regenerate items_summary
    summary_lines = []
    for item in getattr(doc, "items", []):
        code = getattr(item, "item_code", "")
        name = getattr(item, "item_name", "")
        qty = getattr(item, "qty", 1)
        name_part = f" - {name}" if name and name != code else ""
        summary_lines.append(f"• {code}{name_part} (Qty: {qty})")
    se_doc.items_summary = "\n".join(summary_lines)

    # 5. Save with flags to skip re-validation of unique SO (since we're re-linking)
    se_doc.flags.ignore_validate = False
    se_doc.save(ignore_permissions=True)

    # 6. Check for bay overlap with new duration and add comment if applicable
    if se_doc.service_bay and se_doc.scheduled_date and se_doc.scheduled_time:
        from induct_shop.api.scheduling import check_bay_availability

        is_available = check_bay_availability(
            service_bay=se_doc.service_bay,
            date=str(se_doc.scheduled_date),
            start_time=se_doc.scheduled_time,
            duration_minutes=se_doc.estimated_duration or 0,
            exclude_entry=se_doc.name,
        )

        if not is_available:
            duration_change = ""
            if old_duration and se_doc.estimated_duration != old_duration:
                duration_change = _(" (duration changed from {0} to {1} minutes)").format(
                    old_duration, se_doc.estimated_duration
                )

            frappe.get_doc(
                doctype="Comment",
                comment_type="Info",
                reference_doctype="Schedule Entry",
                reference_name=se_doc.name,
                content=_(
                    "⚠️ <b>Bay Overlap Detected</b>: Sales Order {0} was amended{1}. "
                    "The updated duration may cause a scheduling conflict on bay <b>{2}</b> "
                    "on {3}. Please review and adjust the schedule."
                ).format(doc.name, duration_change, se_doc.service_bay, se_doc.scheduled_date),
            ).insert(ignore_permissions=True)

            frappe.msgprint(
                _("Schedule Entry {0} has been updated to 'Needs Review'. "
                  "A bay overlap was detected — please review the schedule.").format(se_doc.name),
                alert=True,
                indicator="orange",
            )
        else:
            frappe.msgprint(
                _("Schedule Entry {0} has been updated to 'Needs Review' due to the Sales Order amendment.").format(
                    se_doc.name
                ),
                alert=True,
                indicator="blue",
            )
