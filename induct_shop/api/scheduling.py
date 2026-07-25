from typing import List, Dict, Optional, Union, Any
from datetime import timedelta, time, datetime
import frappe
from frappe import _


def to_timedelta(val: Union[str, time, timedelta, int, float, None]) -> timedelta:
    """
    Converts various time representations into a datetime.timedelta object (seconds/minutes from midnight).
    """
    if val is None:
        return timedelta(0)
    if isinstance(val, timedelta):
        return val
    if isinstance(val, time):
        return timedelta(hours=val.hour, minutes=val.minute, seconds=val.second)
    if isinstance(val, (int, float)):
        return timedelta(seconds=int(val))
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return timedelta(0)
        parts = val.split(":")
        try:
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            seconds = int(float(parts[2])) if len(parts) > 2 else 0
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except (ValueError, IndexError):
            return timedelta(0)
    return timedelta(0)


def format_timedelta(td: timedelta) -> str:
    """Formats a timedelta object into a HH:MM string."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def get_shop_settings() -> Dict[str, Any]:
    """Helper to fetch Shop Settings defaults or active record."""
    settings = {
        "operating_hours_start": timedelta(hours=8),
        "operating_hours_end": timedelta(hours=17),
        "break_start": timedelta(hours=12),
        "break_end": timedelta(hours=12, minutes=30),
        "default_slot_interval": 30,
        "enable_technician_capacity": 1,
    }

    if frappe.db.exists("DocType", "Shop Settings"):
        try:
            doc = frappe.get_single("Shop Settings")
            if doc.operating_hours_start:
                settings["operating_hours_start"] = to_timedelta(doc.operating_hours_start)
            if doc.operating_hours_end:
                settings["operating_hours_end"] = to_timedelta(doc.operating_hours_end)
            if doc.break_start:
                settings["break_start"] = to_timedelta(doc.break_start)
            else:
                settings["break_start"] = None
            if doc.break_end:
                settings["break_end"] = to_timedelta(doc.break_end)
            else:
                settings["break_end"] = None
            if doc.default_slot_interval:
                settings["default_slot_interval"] = int(doc.default_slot_interval)
            if hasattr(doc, "enable_technician_capacity"):
                settings["enable_technician_capacity"] = doc.enable_technician_capacity
        except Exception:
            pass

    return settings


@frappe.whitelist()
def effective_end_time(
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    break_start: Union[str, time, timedelta, None] = None,
    break_end: Union[str, time, timedelta, None] = None,
) -> timedelta:
    """
    Calculates the clock-time end of a job, inserting the lunch break if the job spans it.

    - start_time: job start time
    - duration_minutes: pure work-minutes (P80 estimate)
    - break_start, break_end: optional overrides. If None, read from Shop Settings.

    If break is configured and job spans into break (start_time < break_start and naive_end > break_start):
      effective_end = naive_end + break_duration
    Otherwise:
      effective_end = naive_end
    """
    start_td = to_timedelta(start_time)
    duration_td = timedelta(minutes=float(duration_minutes or 0))
    naive_end = start_td + duration_td

    if break_start is None or break_end is None:
        settings = get_shop_settings()
        bs_td = settings["break_start"] if break_start is None else to_timedelta(break_start)
        be_td = settings["break_end"] if break_end is None else to_timedelta(break_end)
    else:
        bs_td = to_timedelta(break_start)
        be_td = to_timedelta(break_end)

    if bs_td and be_td and be_td > bs_td:
        break_duration = be_td - bs_td
        if start_td < bs_td and naive_end > bs_td:
            return naive_end + break_duration

    return naive_end


@frappe.whitelist()
def check_bay_availability(
    service_bay: str,
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    exclude_entry: Optional[str] = None,
) -> bool:
    """
    Checks if a Service Bay is available for a given date, start_time, and duration window.
    Accounts for lunch breaks on both the proposed entry and existing entries.
    """
    if not service_bay or not date:
        return False

    settings = get_shop_settings()
    bs_td = settings["break_start"]
    be_td = settings["break_end"]

    prop_start = to_timedelta(start_time)
    prop_end = effective_end_time(prop_start, duration_minutes, bs_td, be_td)

    filters = [
        ["service_bay", "=", service_bay],
        ["scheduled_date", "=", date],
        ["status", "!=", "Cancelled"],
    ]
    if exclude_entry:
        filters.append(["name", "!=", exclude_entry])

    existing_entries = frappe.get_all(
        "Schedule Entry",
        filters=filters,
        fields=["name", "scheduled_time", "estimated_duration"],
    )

    for entry in existing_entries:
        ex_start = to_timedelta(entry.get("scheduled_time"))
        ex_duration = entry.get("estimated_duration") or 0
        ex_end = effective_end_time(ex_start, ex_duration, bs_td, be_td)

        # Interval overlap check: max(start1, start2) < min(end1, end2)
        if max(prop_start, ex_start) < min(prop_end, ex_end):
            return False

    return True


@frappe.whitelist()
def get_available_bays(
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    required_tags: Optional[Union[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Returns a list of active Service Bays that match required equipment tags and are free
    during the proposed lunch-aware time window.
    """
    if isinstance(required_tags, str):
        try:
            required_tags = frappe.parse_json(required_tags)
        except Exception:
            required_tags = [t.strip() for t in required_tags.split(",") if t.strip()]
    if not required_tags:
        required_tags = []

    required_tags_set = set(required_tags)

    active_bays = frappe.get_all(
        "Service Bay",
        filters={"is_active": 1},
        fields=["name", "bay_name"],
    )

    available_bays = []
    for bay in active_bays:
        bay_name = bay.get("bay_name") or bay.get("name")
        # Fetch equipment tags
        tags = frappe.get_all(
            "Service Bay Equipment",
            filters={"parent": bay.get("name")},
            pluck="equipment_tag",
        )
        bay_tags_set = set(tags)

        if not required_tags_set.issubset(bay_tags_set):
            continue

        if check_bay_availability(bay_name, date, start_time, duration_minutes):
            available_bays.append({
                "bay_name": bay_name,
                "equipment_tags": tags,
            })

    return available_bays


@frappe.whitelist()
def auto_assign_bay(
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    required_tags: Optional[Union[str, List[str]]] = None,
) -> str:
    """
    Auto-assigns the first available capable Service Bay for the chosen time window.
    Raises ValidationError if no capable bay is free or if technician pool is exhausted.
    """
    settings = get_shop_settings()
    if settings.get("enable_technician_capacity"):
        from induct_shop.api.technician_availability import get_technician_pool_availability
        pool = get_technician_pool_availability(date, start_time, duration_minutes)
        if not pool.get("is_available"):
            frappe.throw(
                _("Technician pool capacity exhausted for the selected time window on {0}.").format(date),
                frappe.ValidationError,
            )

    bays = get_available_bays(date, start_time, duration_minutes, required_tags)
    if not bays:
        frappe.throw(
            _("No available service bay with required equipment for the selected time window."),
            frappe.ValidationError,
        )
    return bays[0]["bay_name"]


@frappe.whitelist()
def get_available_slots(
    date: str,
    duration_minutes: Union[int, float],
    required_tags: Optional[Union[str, List[str]]] = None,
    service_bay: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Returns available slot dicts for a given date and duration across shop operating hours.
    Excludes lunch break slots and slots ending after operating hours.
    """
    settings = get_shop_settings()
    op_start = settings["operating_hours_start"]
    op_end = settings["operating_hours_end"]
    bs_td = settings["break_start"]
    be_td = settings["break_end"]
    interval = settings["default_slot_interval"]
    enable_tech = settings.get("enable_technician_capacity")

    curr_time = op_start
    slots = []

    duration_val = float(duration_minutes or 0)

    while curr_time < op_end:
        # 1. Skip slot if curr_time falls inside lunch break
        if bs_td and be_td and curr_time >= bs_td and curr_time < be_td:
            curr_time += timedelta(minutes=interval)
            continue

        # 2. Check effective end time
        eff_end = effective_end_time(curr_time, duration_val, bs_td, be_td)
        if eff_end > op_end:
            curr_time += timedelta(minutes=interval)
            continue

        # 3. Check bay availability
        if service_bay:
            if check_bay_availability(service_bay, date, curr_time, duration_val):
                avail_bays_count = 1
            else:
                avail_bays_count = 0
        else:
            avail_bays = get_available_bays(date, curr_time, duration_val, required_tags)
            avail_bays_count = len(avail_bays)

        # 4. Check technician capacity if enabled
        if enable_tech:
            from induct_shop.api.technician_availability import get_technician_pool_availability
            tech_pool = get_technician_pool_availability(date, curr_time, duration_val)
            avail_techs_count = tech_pool.get("available", 0)
            eff_cap = min(avail_bays_count, avail_techs_count)
            if avail_techs_count < avail_bays_count:
                bottleneck = "technicians"
            elif avail_bays_count < avail_techs_count:
                bottleneck = "bays"
            else:
                bottleneck = None
        else:
            avail_techs_count = None
            eff_cap = avail_bays_count
            bottleneck = None

        if eff_cap > 0:
            slots.append({
                "start_time": format_timedelta(curr_time),
                "available_bays": avail_bays_count,
                "available_technicians": avail_techs_count,
                "effective_capacity": eff_cap,
                "bottleneck": bottleneck,
            })

        curr_time += timedelta(minutes=interval)

    return slots

