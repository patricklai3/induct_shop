from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date, time, timedelta
import json
import frappe
from frappe import _
from induct_shop.api.scheduling import (
    to_timedelta,
    get_shop_settings,
    effective_end_time,
)


STATUS_COLOR_MAP = {
    "Scheduled": "#2b6cb0",
    "In Progress": "#d69e2e",
    "Needs Review": "#dc3545",
    "Completed": "#28a745",
    "Cancelled": "#6c757d",
    "Draft": "#718096",
}


def resolve_vehicle_info(doc: Dict[str, Any]) -> str:
    """
    Dynamically resolves vehicle information by traversing linked Project / Sales Order,
    formatting it as 'Model Year Model Trim' (or fallback name/license plate) instead of raw VIN.
    """
    vehicle_id = doc.get("repair_vehicle")

    # 1. Resolve vehicle link from Project or Sales Order if missing on Schedule Entry
    if not vehicle_id:
        project_id = doc.get("project")
        if not project_id and doc.get("sales_order"):
            project_id = frappe.db.get_value("Project", {"sales_order": doc.get("sales_order")})
            if not project_id:
                project_id = frappe.db.get_value(
                    "Sales Order Item",
                    {"parent": doc.get("sales_order"), "project": ["is", "set"]},
                    "project",
                )

        if project_id:
            if frappe.db.has_column("Project", "custom_repair_vehicle"):
                vehicle_id = frappe.db.get_value("Project", project_id, "custom_repair_vehicle")
            elif frappe.db.has_column("Project", "repair_vehicle"):
                vehicle_id = frappe.db.get_value("Project", project_id, "repair_vehicle")

        if not vehicle_id and doc.get("sales_order"):
            if frappe.db.has_column("Sales Order", "custom_repair_vehicle"):
                vehicle_id = frappe.db.get_value("Sales Order", doc.get("sales_order"), "custom_repair_vehicle")
            elif frappe.db.has_column("Sales Order", "repair_vehicle"):
                vehicle_id = frappe.db.get_value("Sales Order", doc.get("sales_order"), "repair_vehicle")

    if not vehicle_id:
        return _("No Vehicle")

    # 2. Format vehicle info into human-readable model/name: e.g., '2021 Model Y'
    if frappe.db.exists("Repair Vehicle", vehicle_id):
        v_details = frappe.db.get_value(
            "Repair Vehicle",
            vehicle_id,
            ["model_year", "manufacturer", "model", "trim", "license_plate"],
            as_dict=True,
        )
        if v_details:
            parts = []
            for field in ("model_year", "model", "trim"):
                val = (v_details.get(field) or "").strip()
                if val and val not in parts:
                    parts.append(val)
            if parts:
                return " ".join(parts)
            if v_details.get("license_plate"):
                return f"Plate: {v_details.get('license_plate')}"

    return str(vehicle_id)


@frappe.whitelist()
def get_calendar_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    filters: Optional[Union[Dict, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Whitelisted API endpoint for Frappe Calendar / FullCalendar to fetch Schedule Entry events.

    Args:
        start: Start date string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        end: End date string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
        filters: Optional dictionary or JSON-string filters for Schedule Entry query

    Returns:
        List of enriched event dictionaries formatted for Calendar view rendering.
    """
    parsed_filters = filters
    if isinstance(filters, str):
        try:
            parsed_filters = json.loads(filters)
        except (ValueError, TypeError):
            parsed_filters = {}

    query_filters = {}
    if isinstance(parsed_filters, dict):
        query_filters = dict(parsed_filters)
    elif isinstance(parsed_filters, list):
        query_filters = {}
        for item in parsed_filters:
            if isinstance(item, list) and len(item) >= 3:
                if len(item) == 4:
                    fieldname = item[1]
                    op = item[2]
                    val = item[3]
                else:
                    fieldname = item[0]
                    op = item[1]
                    val = item[2]
                if op == "=":
                    query_filters[fieldname] = val
                else:
                    query_filters[fieldname] = [op, val]

    # Date range filtering
    start_date = None
    end_date = None

    if start:
        start_str = start.split(" ")[0].split("T")[0]
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    if end:
        end_str = end.split(" ")[0].split("T")[0]
        try:
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    or_filters = []
    if start_date and end_date:
        query_filters["scheduled_date"] = ["between", [start_date, end_date]]
    elif start_date:
        query_filters["scheduled_date"] = [">=", start_date]
    elif end_date:
        query_filters["scheduled_date"] = ["<=", end_date]

    entries = frappe.get_all(
        "Schedule Entry",
        filters=query_filters,
        fields=[
            "name",
            "customer",
            "repair_vehicle",
            "project",
            "scheduled_date",
            "scheduled_time",
            "estimated_duration",
            "service_bay",
            "assigned_technician",
            "status",
            "items_summary",
            "sales_order",
        ],
        order_by="scheduled_date asc, scheduled_time asc",
    )

    settings = get_shop_settings()
    bs_td = settings.get("break_start")
    be_td = settings.get("break_end")

    events = []

    for doc in entries:
        if not doc.scheduled_date or not doc.scheduled_time:
            continue

        entry_date = doc.scheduled_date
        if isinstance(entry_date, str):
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()

        start_td = to_timedelta(doc.scheduled_time)
        start_seconds = int(start_td.total_seconds())
        start_datetime = datetime.combine(entry_date, time(0, 0)) + timedelta(seconds=start_seconds)

        duration_mins = doc.estimated_duration or 0
        eff_end_td = effective_end_time(
            start_time=doc.scheduled_time,
            duration_minutes=duration_mins,
            break_start=bs_td,
            break_end=be_td,
        )
        eff_end_seconds = int(eff_end_td.total_seconds())
        end_datetime = datetime.combine(entry_date, time(0, 0)) + timedelta(seconds=eff_end_seconds)

        # Determine if job spans lunch break
        naive_end_td = start_td + timedelta(minutes=duration_mins)
        spans_lunch = bool(
            bs_td and be_td and be_td > bs_td and start_td < bs_td and naive_end_td > bs_td
        )

        customer_name = doc.customer or _("No Customer")
        vehicle_display = resolve_vehicle_info(doc)
        bay_name = doc.service_bay or _("Unassigned Bay")
        tech_name = doc.assigned_technician or _("Unassigned Tech")

        title = f"{customer_name} | {vehicle_display} ({bay_name})"

        color = STATUS_COLOR_MAP.get(doc.status, "#718096")

        events.append(
            {
                "name": doc.name,
                "id": doc.name,
                "title": title,
                "start": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "scheduled_date": str(entry_date),
                "scheduled_time": str(doc.scheduled_time),
                "estimated_duration": duration_mins,
                "status": doc.status or "Scheduled",
                "customer": doc.customer,
                "repair_vehicle": vehicle_display,
                "service_bay": doc.service_bay,
                "assigned_technician": doc.assigned_technician,
                "items_summary": doc.items_summary or "",
                "sales_order": doc.sales_order,
                "spans_lunch": spans_lunch,
                "color": color,
                "allDay": 0,
            }
        )

    return events

