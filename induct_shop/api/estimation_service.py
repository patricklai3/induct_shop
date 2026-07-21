import frappe
from induct_shop.scheduling.estimation_light import (
    estimate_duration,
    estimate_total_duration,
    get_sigma_for_item,
)


@frappe.whitelist()
def get_estimate(item_code: str, **kwargs) -> int:
    """Get the P80 duration estimate for a single operation."""
    frt = _get_frt(item_code)
    item_group = frappe.db.get_value("Item", item_code, "item_group")
    sigma = get_sigma_for_item(item_group)
    return estimate_duration(frt, sigma=sigma)


@frappe.whitelist()
def get_total_estimate(item_codes: str, **kwargs) -> int:
    """
    Get the P80 total duration estimate for multiple operations.
    Accepts item_codes as a JSON string list or Python list.
    """
    if isinstance(item_codes, str):
        try:
            item_codes = frappe.parse_json(item_codes)
        except Exception:
            # Fallback if comma-separated
            item_codes = [c.strip() for c in item_codes.split(",")]

    operations = []
    for code in item_codes:
        frt = _get_frt(code)
        item_group = frappe.db.get_value("Item", code, "item_group")
        sigma = get_sigma_for_item(item_group)
        operations.append({"frt_minutes": frt, "sigma": sigma})
    
    return estimate_total_duration(operations)


def _get_frt(item_code: str) -> float:
    """Safely retrieve FRT, falling back to a default."""
    if frappe.db.has_column("Item", "custom_frt"):
        frt = frappe.db.get_value("Item", item_code, "custom_frt")
        if frt and float(frt) > 0:
            return float(frt)
    return 60.0  # Default fallback: 1 hour
