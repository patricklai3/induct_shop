from typing import List, Union, Dict, Optional, Any
import frappe
from induct_shop.scheduling.estimation_light import (
    estimate_duration,
    estimate_total_duration,
    get_sigma_for_item,
    DEFAULT_SIGMA,
)


@frappe.whitelist()
def get_estimate(item_code: str, **kwargs) -> int:
    """
    Get the P80 duration estimate for a single operation.

    Args:
        item_code: Item code to look up in Frappe database.
        **kwargs:
            - fallback_frt: Default FRT in minutes if item/custom_frt missing.
            - sigma: Custom sigma override.
            - percentile: Target percentile (default 0.80).
    """
    fallback_frt = kwargs.get("fallback_frt", 60.0)
    if isinstance(fallback_frt, str):
        fallback_frt = float(fallback_frt) if fallback_frt else None

    frt = _get_frt(item_code, fallback=fallback_frt)

    if frt is None or frt <= 0:
        return 0

    item_group = frappe.db.get_value("Item", item_code, "item_group") if frappe.db.exists("Item", item_code) else None
    sigma = kwargs.get("sigma")
    if sigma is None:
        sigma = get_sigma_for_item(item_group)
    else:
        sigma = float(sigma)

    percentile = float(kwargs.get("percentile", 0.80))
    return estimate_duration(frt, sigma=sigma, percentile=percentile)


@frappe.whitelist()
def get_total_estimate(item_codes: Union[str, List[Union[str, Dict[str, Any]]]], **kwargs) -> int:
    """
    Get the P80 total duration estimate for multiple operations using Fenton-Wilkinson summation.

    Args:
        item_codes: JSON string list, Python list of item codes, or list of operation dicts.
        **kwargs:
            - fallback_frt: Default FRT in minutes for missing items (default 60.0).
            - skip_missing: If True, omit items without valid FRT.
            - sigma: Custom default sigma override.
            - percentile: Target percentile (default 0.80).
    """
    if isinstance(item_codes, str):
        try:
            item_codes = frappe.parse_json(item_codes)
        except Exception:
            item_codes = [c.strip() for c in item_codes.split(",") if c.strip()]

    if not item_codes:
        return 0

    fallback_frt = kwargs.get("fallback_frt", 60.0)
    if isinstance(fallback_frt, str):
        fallback_frt = float(fallback_frt) if fallback_frt else None

    skip_missing = kwargs.get("skip_missing", False)
    if isinstance(skip_missing, str):
        skip_missing = skip_missing.lower() in ("true", "1")
    else:
        skip_missing = bool(skip_missing)

    default_sigma = kwargs.get("sigma")
    percentile = float(kwargs.get("percentile", 0.80))

    operations = []
    for item in item_codes:
        if isinstance(item, dict):
            code = item.get("item_code")
            item_frt = item.get("flat_rate_minutes") or item.get("frt_minutes")
            item_sig = item.get("sigma")
        else:
            code = str(item)
            item_frt = None
            item_sig = None

        if item_frt is None and code:
            effective_fallback = None if skip_missing else fallback_frt
            item_frt = _get_frt(code, fallback=effective_fallback)

        if item_frt is None or item_frt <= 0:
            if skip_missing:
                continue
            item_frt = fallback_frt if fallback_frt and fallback_frt > 0 else None

        if item_frt is None or item_frt <= 0:
            continue

        if item_sig is None:
            if default_sigma is not None:
                item_sig = float(default_sigma)
            elif code and frappe.db.exists("Item", code):
                item_group = frappe.db.get_value("Item", code, "item_group")
                item_sig = get_sigma_for_item(item_group)
            else:
                item_sig = DEFAULT_SIGMA

        operations.append({"flat_rate_minutes": float(item_frt), "sigma": float(item_sig)})

    if not operations:
        return 0

    return estimate_total_duration(operations, percentile=percentile)


def _get_frt(item_code: str, fallback: Optional[float] = 60.0) -> Optional[float]:
    """Safely retrieve FRT from Item DocType, checking column existence defensively."""
    if not item_code:
        return fallback

    if frappe.db.has_column("Item", "custom_frt"):
        if frappe.db.exists("Item", item_code):
            frt = frappe.db.get_value("Item", item_code, "custom_frt")
            if frt is not None:
                try:
                    val = float(frt)
                    if val > 0:
                        return val
                except (ValueError, TypeError):
                    pass

    return fallback


