from typing import List, Dict, Optional, Union, Any
from datetime import timedelta, time, datetime
import frappe
from frappe import _

from induct_shop.api.scheduling import (
    to_timedelta,
    format_timedelta,
    get_shop_settings,
    effective_end_time,
)


@frappe.whitelist()
def get_active_technicians(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns active employees matching Shop Settings -> technician_designation.
    If date is provided, includes leave status from approved Leave Applications.
    """
    settings = get_shop_settings()
    designation = settings.get("technician_designation") or "Technician"

    employees = frappe.get_all(
        "Employee",
        filters={
            "designation": designation,
            "status": "Active",
        },
        fields=["name", "employee_name", "designation"],
    )

    results = []
    target_date = str(date) if date else None

    # Fetch approved leave applications for target_date if date provided
    leave_map = {}
    if target_date and frappe.db.exists("DocType", "Leave Application"):
        leaves = frappe.get_all(
            "Leave Application",
            filters=[
                ["status", "=", "Approved"],
                ["docstatus", "=", 1],
                ["from_date", "<=", target_date],
                ["to_date", ">=", target_date],
            ],
            fields=["employee", "half_day", "half_day_date"],
        )
        for l in leaves:
            leave_map[l.employee] = l

    for emp in employees:
        emp_id = emp["name"]
        leave_info = leave_map.get(emp_id)
        is_on_leave = False
        is_half_day = False

        if leave_info:
            is_half_day = bool(leave_info.get("half_day"))
            half_day_date = str(leave_info.get("half_day_date")) if leave_info.get("half_day_date") else None
            if is_half_day:
                if half_day_date == target_date:
                    is_on_leave = True
            else:
                is_on_leave = True

        results.append({
            "employee": emp_id,
            "employee_name": emp.get("employee_name") or emp_id,
            "on_leave": is_on_leave,
            "half_day": is_half_day,
        })

    return results


def check_employee_leave(
    employee: str,
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
) -> Dict[str, Any]:
    """
    Internal helper to check if an employee is on leave during a specific slot on date.
    """
    if not frappe.db.exists("DocType", "Leave Application"):
        return {"on_leave": False, "half_day": False}

    leaves = frappe.get_all(
        "Leave Application",
        filters=[
            ["employee", "=", employee],
            ["status", "=", "Approved"],
            ["docstatus", "=", 1],
            ["from_date", "<=", date],
            ["to_date", ">=", date],
        ],
        fields=["name", "half_day", "half_day_date"],
    )

    if not leaves:
        return {"on_leave": False, "half_day": False}

    settings = get_shop_settings()
    bs_td = settings["break_start"] or timedelta(hours=12)

    for l in leaves:
        is_half_day = bool(l.get("half_day"))
        half_day_date = str(l.get("half_day_date")) if l.get("half_day_date") else None

        if not is_half_day:
            return {"on_leave": True, "half_day": False}

        if half_day_date == date:
            return {"on_leave": True, "half_day": True}

    return {"on_leave": False, "half_day": False}


@frappe.whitelist()
def get_technician_pool_availability(
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    exclude_entry: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Pool-level gating function. Checks how many total, on-duty, occupied, and available technicians exist.
    """
    settings = get_shop_settings()
    if not settings.get("enable_technician_capacity"):
        return {
            "total_technicians": 999,
            "on_leave": 0,
            "on_duty": 999,
            "occupied": 0,
            "available": 999,
            "is_available": True,
        }

    technicians = get_active_technicians(date=date)
    total_techs = len(technicians)
    if total_techs == 0:
        return {
            "total_technicians": 0,
            "on_leave": 0,
            "on_duty": 0,
            "occupied": 0,
            "available": 0,
            "is_available": False,
        }

    bs_td = settings["break_start"]
    be_td = settings["break_end"]
    prop_start = to_timedelta(start_time)
    prop_end = effective_end_time(prop_start, duration_minutes, bs_td, be_td)

    on_leave_count = 0
    on_duty_techs = []

    for tech in technicians:
        emp_id = tech["employee"]
        leave_res = check_employee_leave(emp_id, date, start_time, duration_minutes)
        if leave_res["on_leave"]:
            on_leave_count += 1
        else:
            on_duty_techs.append(emp_id)

    on_duty_count = len(on_duty_techs)
    occupied_count = 0

    if on_duty_techs:
        # Check entries for on-duty technicians during this time window
        filters = [
            ["assigned_technician", "in", on_duty_techs],
            ["scheduled_date", "=", date],
            ["status", "!=", "Cancelled"],
        ]
        if exclude_entry:
            filters.append(["name", "!=", exclude_entry])

        entries = frappe.get_all(
            "Schedule Entry",
            filters=filters,
            fields=["assigned_technician", "scheduled_time", "estimated_duration"],
        )

        occupied_techs = set()
        for entry in entries:
            ex_start = to_timedelta(entry.get("scheduled_time"))
            ex_duration = entry.get("estimated_duration") or 0
            ex_end = effective_end_time(ex_start, ex_duration, bs_td, be_td)

            if max(prop_start, ex_start) < min(prop_end, ex_end):
                occupied_techs.add(entry.get("assigned_technician"))

        occupied_count = len(occupied_techs)

    available_count = max(0, on_duty_count - occupied_count)

    return {
        "total_technicians": total_techs,
        "on_leave": on_leave_count,
        "on_duty": on_duty_count,
        "occupied": occupied_count,
        "available": available_count,
        "is_available": available_count > 0,
    }


@frappe.whitelist()
def check_technician_availability(
    employee: str,
    date: str,
    start_time: Union[str, time, timedelta],
    duration_minutes: Union[int, float],
    exclude_entry: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Checks availability of a specific technician for a given date/time window.
    Returns details on leave status, overlaps, and availability.
    """
    if not employee or not date:
        return {
            "is_available": False,
            "reason": "invalid_parameters",
            "on_leave": False,
            "half_day": False,
            "conflicts": [],
        }

    # Verify technician active & designation match
    settings = get_shop_settings()
    designation = settings.get("technician_designation") or "Technician"

    emp_doc = frappe.db.get_value(
        "Employee",
        employee,
        ["status", "designation"],
        as_dict=True,
    )

    if not emp_doc or emp_doc.status != "Active":
        return {
            "is_available": False,
            "reason": "inactive",
            "on_leave": False,
            "half_day": False,
            "conflicts": [],
        }

    if emp_doc.designation != designation:
        return {
            "is_available": False,
            "reason": "designation_mismatch",
            "on_leave": False,
            "half_day": False,
            "conflicts": [],
        }

    # Check leave status
    leave_res = check_employee_leave(employee, date, start_time, duration_minutes)
    if leave_res["on_leave"]:
        return {
            "is_available": False,
            "reason": "on_leave",
            "on_leave": True,
            "half_day": leave_res["half_day"],
            "conflicts": [],
        }

    # Check overlapping schedule entries
    bs_td = settings["break_start"]
    be_td = settings["break_end"]
    prop_start = to_timedelta(start_time)
    prop_end = effective_end_time(prop_start, duration_minutes, bs_td, be_td)

    filters = [
        ["assigned_technician", "=", employee],
        ["scheduled_date", "=", date],
        ["status", "!=", "Cancelled"],
    ]
    if exclude_entry:
        filters.append(["name", "!=", exclude_entry])

    existing_entries = frappe.get_all(
        "Schedule Entry",
        filters=filters,
        fields=["name", "scheduled_time", "estimated_duration", "customer", "service_bay"],
    )

    conflicts = []
    for entry in existing_entries:
        ex_start = to_timedelta(entry.get("scheduled_time"))
        ex_duration = entry.get("estimated_duration") or 0
        ex_end = effective_end_time(ex_start, ex_duration, bs_td, be_td)

        if max(prop_start, ex_start) < min(prop_end, ex_end):
            conflicts.append({
                "name": entry.get("name"),
                "scheduled_time": format_timedelta(ex_start),
                "estimated_duration": ex_duration,
                "effective_end_time": format_timedelta(ex_end),
                "customer": entry.get("customer"),
                "service_bay": entry.get("service_bay"),
            })

    if conflicts:
        return {
            "is_available": False,
            "reason": "overlap",
            "on_leave": False,
            "half_day": False,
            "conflicts": conflicts,
        }

    return {
        "is_available": True,
        "reason": None,
        "on_leave": False,
        "half_day": False,
        "conflicts": [],
    }


@frappe.whitelist()
def get_technician_queue(employee: str, date: str) -> Dict[str, Any]:
    """
    Returns personal work queue for a technician on a specific date.
    Calculates gaps between entries and utilization percentage.
    """
    settings = get_shop_settings()
    op_start = settings["operating_hours_start"]
    op_end = settings["operating_hours_end"]
    bs_td = settings["break_start"]
    be_td = settings["break_end"]

    emp_name = frappe.db.get_value("Employee", employee, "employee_name") or employee

    # Check leave status
    leave_res = check_employee_leave(employee, date, op_start, 0)
    on_leave = leave_res["on_leave"]

    entries = frappe.get_all(
        "Schedule Entry",
        filters=[
            ["assigned_technician", "=", employee],
            ["scheduled_date", "=", date],
            ["status", "!=", "Cancelled"],
        ],
        fields=[
            "name",
            "scheduled_time",
            "estimated_duration",
            "service_bay",
            "customer",
            "repair_vehicle",
            "items_summary",
            "status",
            "sales_order",
        ],
        order_by="scheduled_time asc",
    )

    formatted_entries = []
    total_minutes = 0
    gaps = []

    last_end_td = op_start

    for entry in entries:
        st_td = to_timedelta(entry.get("scheduled_time"))
        dur = entry.get("estimated_duration") or 0
        eff_end_td = effective_end_time(st_td, dur, bs_td, be_td)

        total_minutes += dur

        # Calculate gap before this entry if there is clear space
        if st_td > last_end_td:
            gap_dur = int((st_td - last_end_td).total_seconds() // 60)
            if bs_td and be_td and last_end_td <= bs_td and st_td >= be_td:
                gap_dur -= int((be_td - bs_td).total_seconds() // 60)
            if gap_dur > 0:
                gaps.append({
                    "after": formatted_entries[-1]["name"] if formatted_entries else "start_of_day",
                    "duration_minutes": gap_dur,
                    "start": format_timedelta(last_end_td),
                })

        formatted_entries.append({
            "name": entry["name"],
            "scheduled_time": format_timedelta(st_td),
            "estimated_duration": dur,
            "effective_end_time": format_timedelta(eff_end_td),
            "service_bay": entry.get("service_bay"),
            "customer": entry.get("customer"),
            "repair_vehicle": entry.get("repair_vehicle"),
            "items_summary": entry.get("items_summary"),
            "status": entry.get("status"),
            "sales_order": entry.get("sales_order"),
        })

        last_end_td = max(last_end_td, eff_end_td)

    shop_op_minutes = int((op_end - op_start).total_seconds() // 60)
    if bs_td and be_td and be_td > bs_td:
        shop_op_minutes -= int((be_td - bs_td).total_seconds() // 60)

    shop_op_minutes = max(1, shop_op_minutes)
    utilization_pct = round((total_minutes / shop_op_minutes) * 100, 1)

    return {
        "employee": employee,
        "employee_name": emp_name,
        "on_leave": on_leave,
        "entries": formatted_entries,
        "total_jobs": len(formatted_entries),
        "total_minutes": total_minutes,
        "utilization_pct": utilization_pct,
        "gaps": gaps,
    }


@frappe.whitelist()
def get_daily_technician_overview(date: str) -> Dict[str, Any]:
    """
    Shop-wide technician dashboard data for managers.
    """
    settings = get_shop_settings()
    op_start = settings["operating_hours_start"]
    op_end = settings["operating_hours_end"]
    bs_td = settings["break_start"]
    be_td = settings["break_end"]

    operating_minutes = int((op_end - op_start).total_seconds() // 60)
    if bs_td and be_td and be_td > bs_td:
        operating_minutes -= int((be_td - bs_td).total_seconds() // 60)
    operating_minutes = max(1, operating_minutes)

    active_techs = get_active_technicians(date=date)

    tech_summaries = []
    total_scheduled_minutes = 0

    for tech in active_techs:
        emp_id = tech["employee"]
        queue = get_technician_queue(emp_id, date)

        tech_summaries.append({
            "employee": emp_id,
            "employee_name": tech["employee_name"],
            "on_leave": tech["on_leave"],
            "job_count": queue["total_jobs"],
            "total_minutes": queue["total_minutes"],
            "utilization_pct": queue["utilization_pct"],
        })
        total_scheduled_minutes += queue["total_minutes"]

    unassigned = frappe.get_all(
        "Schedule Entry",
        filters=[
            ["scheduled_date", "=", date],
            ["status", "!=", "Cancelled"],
            ["assigned_technician", "is", "not set"],
        ],
        fields=["name", "scheduled_time", "customer", "repair_vehicle", "service_bay", "estimated_duration"],
    )

    unassigned_formatted = []
    for u in unassigned:
        st_td = to_timedelta(u.get("scheduled_time"))
        unassigned_formatted.append({
            "name": u["name"],
            "scheduled_time": format_timedelta(st_td),
            "customer": u.get("customer"),
            "repair_vehicle": u.get("repair_vehicle"),
            "service_bay": u.get("service_bay"),
            "estimated_duration": u.get("estimated_duration") or 0,
        })

    total_bays = frappe.db.count("Service Bay", {"is_active": 1})
    on_duty_count = sum(1 for t in tech_summaries if not t["on_leave"])
    on_leave_count = sum(1 for t in tech_summaries if t["on_leave"])

    bottleneck = "technicians" if on_duty_count < total_bays else ("bays" if total_bays < on_duty_count else None)

    return {
        "date": date,
        "operating_minutes": operating_minutes,
        "technicians": tech_summaries,
        "unassigned_entries": unassigned_formatted,
        "shop_summary": {
            "total_technicians": len(active_techs),
            "on_duty": on_duty_count,
            "on_leave": on_leave_count,
            "total_bays": total_bays,
            "bottleneck": bottleneck,
            "total_scheduled_hours": round(total_scheduled_minutes / 60.0, 1),
            "unassigned_count": len(unassigned_formatted),
        },
    }
