---
type: Specification
title: "Scheduling System"
description: "Comprehensive specification for the Induct Shop scheduling system, covering FRT-based lightweight estimation, Sales Order-driven scheduling, dual-resource (bay + technician) capacity management, lunch-aware time windows, and staff-facing UI."
status: Proposed
tags: [system, scheduling, estimation, specification, log-normal, capacity, technician]
timestamp: 2026-07-23T21:48:00Z
---

# Scheduling System

The scheduling system provides duration estimation for automotive repair operations and manages shop capacity to prevent overbooking. It is built in three layers: a **pure-Python estimation engine**, a **Frappe integration layer** that exposes estimates through the existing ERPNext workflow, and a **scheduling layer** that generates and manages Schedule Entries from confirmed Sales Orders.

> [!NOTE]
> This specification describes a **Lightweight FRT-Based Estimator (Phase 1)** paired with a **dual-resource capacity model** (bays + technicians). Customer-facing appointment booking is deferred to a future customer portal integration — this system focuses exclusively on backend logic and the staff-facing UI.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Sales Order (submitted, docstatus=1)               │
│       Contains: Services (w/ FRT), Parts, Project link              │
│       Staff clicks "Schedule Service" button                        │
└────────────────────────┬────────────────────────────────────────────┘
                         │ generates (1:1)
┌────────────────────────▼────────────────────────────────────────────┐
│                   Schedule Entry (New DocType)                       │
│                                                                     │
│  Links: Sales Order, Project, Customer, Repair Vehicle              │
│  Fields: scheduled_date, scheduled_time, estimated_duration,        │
│          service_bay (required), assigned_technician (encouraged),   │
│          status                                                     │
│  Duration: auto-calculated via estimation_service.get_total_estimate│
└────────────────────────┬────────────────────────────────────────────┘
                         │ validated against
┌────────────────────────▼────────────────────────────────────────────┐
│              Dual-Resource Capacity Layer                            │
│                                                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐  │
│  │  Bay Capacity         │    │  Technician Capacity              │  │
│  │                       │    │                                   │  │
│  │  Service Bay DocType  │    │  Employee (designation filter)    │  │
│  │  Per-bay overlap      │    │  Shared shop hours (Shop Settings)│  │
│  │  (hard enforce)       │    │  HRMS Leave Application → leave   │  │
│  │  Equipment tag match  │    │    exclusion from pool            │  │
│  │  Auto-assign bay      │    │  Pool-level gating (hard)         │  │
│  │                       │    │  Individual overlap (soft warn)   │  │
│  └──────────────────────┘    └──────────────────────────────────┘  │
│                                                                     │
│  effective_capacity(T) = min(free_bays(T), available_technicians)  │
│  Slot available only if effective_capacity ≥ 1                     │
│                                                                     │
│  Lunch-Aware Time Windows:                                          │
│  Jobs spanning the break window have break duration added to their  │
│  effective end time. All overlap checks use lunch-aware end times.  │
└─────────────────────────────────────────────────────────────────────┘
                         │ surfaced via
┌────────────────────────▼────────────────────────────────────────────┐
│                   Staff-Facing UI                                    │
│                                                                     │
│  Calendar view        → day/week schedule, color-coded statuses     │
│  List view            → filterable, sortable schedule list          │
│  Schedule Service     → slot picker with dual-resource indicators   │
│  Shop Floor Dashboard → bay lanes + technician load panel           │
│  Technician Daily     → personal timeline + "Next Up"              │
└─────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Decoupled engine** — The estimation math has zero Frappe dependencies. It can be unit-tested and reasoned about in isolation.
2. **Sales Order as the source of truth** — The Sales Order is a confirmation of service that contains all necessary services and parts. Schedule Entries are always generated from a submitted Sales Order.
3. **Per-bay capacity model** — Each Schedule Entry is assigned to a specific Service Bay. Overbooking prevention ensures no two entries overlap on the same bay. Bays have capability flags (e.g., `has_lift`) so staff can match jobs to appropriate bays.
4. **1:1 relationship** — Each Sales Order maps to exactly one Schedule Entry. Follow-up visits require a new Sales Order.
5. **P80 as the scheduling block** — The log-normal P80 estimate provides a conservative built-in buffer. No additional buffer is applied on top.
6. **Dual-resource gating** — Shop capacity is bounded by both bays and technicians. Scheduling is gated against the bottleneck resource. Technicians share the shop operating hours and the system uses HRMS Leave Applications to exclude absent staff from the available pool.

---

## 2. Estimation Engine (Phase 1: Lightweight Log-Normal)

### 2.1 Mathematical Foundation

The engine uses a simple right-skewed (log-normal) distribution anchored at the FRT, extracting the 80th percentile as the risk-adjusted estimate.

- **Median**: The FRT (from the Tesla Service Manual) is treated as the median (P50) of the distribution.
- **Shape Parameter (σ)**: A single fixed shape parameter (σ=0.30) controls the skewness. This value provides a reasonable buffer across all operation types without per-category tuning.
- **Extraction**: The P80 is extracted analytically.

For a 60-minute FRT with σ=0.30:

- P80 ≈ 77.2 minutes (+29% buffer)
- P50 (median) = 60 min
- P95 ≈ 99.5 min

### 2.2 Multi-Operation Summation

When a vehicle has multiple operations on a single visit, the total estimated duration accounts for the fact that individual variances partially cancel when summed (diversification effect). Naively summing individual P80s is overly conservative.

The engine uses the **Fenton-Wilkinson approximation** to fit a single log-normal to the sum of independent log-normal distributions, providing a tighter and more accurate P80 for the total visit.

### 2.3 Future Bayesian Engine (Phase 2)

The lightweight estimator is a strong Day-1 strategy, but it lacks learning capabilities. 
In Phase 2, once a task-completion tracking mechanism is built in Frappe, the system will migrate to a **Sequential Bayesian Linear Regression** engine. This future engine will learn from historical completions and adapt to specific vehicle ages, mileages, and technicians.

The `estimation_light.py` functions are designed to be drop-in replaceable by the future Bayesian `get_estimate()` API.

---

## 3. Frappe Integration Layer

### 3.1 Data Sources (Existing)

All estimator inputs map to fields that already exist in the Induct Shop schema:

| Estimator Input | Frappe Source | Field |
|---|---|---|
| `flat_rate_minutes` | Item | `custom_frt` (custom field, populated during service ingestion) |
| `item_code` | Item | `item_code` (Tesla Correction Code) |

### 3.2 Estimation Service API

A Python module (`induct_shop.api.estimation_service`) providing core functions for external callers (scheduling, quoting):

**`get_estimate(item_code: str, **kwargs) -> int`**
- Retrieves the FRT for the item.
- Applies the fixed σ=0.30.
- Returns the P80 duration in minutes.

**`get_total_estimate(item_codes: list[str], **kwargs) -> int`**
- Gathers FRT for all provided item codes (all using fixed σ=0.30).
- Implements Fenton-Wilkinson summation.
- Returns the total P80 duration in minutes.

> [!IMPORTANT]
> The integration must defensively check for the existence of `custom_frt` using `frappe.db.has_column("Item", "custom_frt")` to prevent SQL errors in environments where migrations haven't run.

---

## 4. Service Bay DocType

A standard DocType (`custom=0, module="Induct Shop"`) representing a physical service bay in the shop.

### 4.1 Schema

| Field | Type | Description |
|---|---|---|
| `bay_name` | Data | Human-readable name (e.g., "Bay 1", "Bay 2 - Lift"). **Required.** Used as the DocType's `title_field`. |
| `equipment` | Table (Service Bay Equipment) | Child table listing the equipment tags provided by this bay (e.g. "Lift", "Alignment Rack"). |
| `is_active` | Check | Whether this bay is currently available for scheduling (default: checked). |
| `description` | Small Text | Optional notes about the bay (e.g., "Rated for Cybertruck weight"). |

### 4.2 Design Notes

- The `bay_name` is the naming field — bays are identified by their human-readable names.
- Bay capabilities are managed dynamically using the tag-based **Equipment Tag** system (`Service Bay Equipment` child table) rather than hardcoded booleans.
- Only bays with `is_active = 1` appear in the scheduling UI and capacity checks.

---

## 5. Schedule Entry DocType

A standard DocType (`custom=0, module="Induct Shop"`) representing a single scheduled appointment / work assignment.

### 5.1 Schema

| Field | Type | Description |
|---|---|---|
| `sales_order` | Link (Sales Order) | The confirmed Sales Order this schedule derives from. **Required.** Unique (enforced 1:1). |
| `project` | Link (Project) | Fetched from the Sales Order. Read Only. |
| `customer` | Link (Customer) | Fetched from the Sales Order. Read Only. |
| `repair_vehicle` | Link (Repair Vehicle) | Fetched from the linked Project. Read Only. |
| `scheduled_date` | Date | The date of the appointment. **Required.** |
| `scheduled_time` | Time | Start time of the appointment. **Required.** |
| `estimated_duration` | Duration | Auto-calculated P80 estimate from all service items on the SO. Represents pure work-minutes (does not include lunch break). |
| `service_bay` | Link (Service Bay) | The specific bay this job is assigned to. **Required.** Drives capacity checks. |
| `assigned_technician` | Link (Employee) | Technician assignment. **Encouraged.** Drives the Technician Work Queue. Not required for scheduling (pool-level gating handles capacity), but expected to be filled before the scheduled date. |
| `status` | Select | `Draft` → `Scheduled` → `Needs Review` → `In Progress` → `Completed` → `Cancelled` |
| `notes` | Small Text | Free-text notes for the service advisor. |
| `items_summary` | Long Text | Read-only auto-generated summary of service items from the SO. |

### 5.2 Controller Logic

- **`before_insert`**: Auto-fetch `project`, `customer`, `repair_vehicle` from the Sales Order and its linked Project.
- **`before_insert`**: Auto-calculate `estimated_duration` by calling `get_total_estimate()` with all service item codes from the linked Sales Order.
- **`validate`**: Call `check_bay_availability()` to verify the assigned bay is free for the chosen date/time/duration window (using the lunch-aware effective end time). Raise `frappe.ValidationError` if the bay is already occupied.
- **`validate`**: If `enable_technician_capacity` is on in Shop Settings, call `get_technician_pool_availability()` to verify the technician pool has capacity. Raise `frappe.ValidationError` if all on-duty technicians are occupied at the proposed time.
- **`validate`**: If `assigned_technician` is set, call `check_technician_availability()` to check for individual overlaps. If the technician is on approved leave, show a **red warning** (via `frappe.msgprint`). If the technician has overlapping Schedule Entries, show an **orange warning**. These are soft warnings — they do not block save.

### 5.3 Relationship Constraint

Each Sales Order maps to exactly one Schedule Entry (1:1). The system enforces this via a unique constraint on the `sales_order` field. The "Schedule Service" button on the Sales Order form is hidden if a Schedule Entry already exists for that SO.

---

## 6. Sales Order Integration

### 6.1 "Schedule Service" Button

A client-side script (`induct_shop/public/js/sales_order.js`) injected into the Sales Order form via the `doctype_js` hook:

- The button appears only when the SO is submitted (`docstatus == 1`) and no Schedule Entry already exists for it.
- On click, opens a simplified **"Schedule Service" slot picker dialog** for front desk staff:
  - **Date Picker** (defaults to today or next business day).
  - **Estimated Duration Badge** (read-only P80 estimate calculated via `get_total_estimate()`).
  - **Available Time Slots**: A grid of clickable time slot buttons generated by `get_available_slots(date, duration, required_tags)`. Unavailable slots and lunch break windows are omitted entirely.
  - **Dual-Resource Capacity Indicator**: Summary text showing slot count and bottleneck (e.g., "10 slots available on July 23 · Bottleneck: Technicians (2 techs limit 4 bays)").
  - **Optional Technician Link**: When a technician is selected and a date/time is chosen, displays their current load for that day (e.g., "Alex Rivera · 3 jobs · 4h 30m · 56% utilized"). If the selected slot overlaps with another assignment for that technician, a yellow warning banner is shown (not a blocker).
  - **Notes** field.
- Front desk staff selects a date and clicks an available time slot. They do **not** select a service bay.
- On submit, the backend invokes `auto_assign_bay()` to select an optimal, capable bay, creates the Schedule Entry with `service_bay` populated programmatically, and navigates to the created record.

### 6.2 Sales Order Amendment Handling

When a Sales Order is amended (a new version is created via ERPNext's Amend flow):

1. The linked Schedule Entry's status is updated to **"Needs Review"** via a `doc_events` hook on Sales Order `on_submit` (for the amended document).
2. The Schedule Entry remains in place with its original date/time/bay slot — it is **not** auto-cancelled.
3. The `estimated_duration` is recalculated from the amended SO's items. If the new duration causes the entry to overlap with another entry on the same bay, a comment is added alerting staff.
4. Staff can then review and manually adjust the schedule or reassign the bay as needed.

---

## 7. Capacity Management

### 7.1 Model: Dual-Resource Capacity

The system uses a **dual-resource capacity model**: each Schedule Entry consumes both a **Service Bay** and a **Technician**. The system ensures that at any given time, no more jobs are scheduled than the shop can simultaneously work on.

- **Bay constraint** (hard, per-bay): Each Schedule Entry is assigned to a specific bay. No two entries may overlap on the same bay. Bay overlap checks use **lunch-aware effective end times** (see §7.3).
- **Technician constraint** (hard, pool-level): The number of overlapping Schedule Entries at any time T cannot exceed the number of available technicians at time T. This prevents the shop from accepting more work than its workforce can handle.
- **Technician assignment constraint** (soft, individual-level): When a specific technician is assigned, the system warns if that technician has an overlapping assignment but allows override with confirmation. This supports real-world scenarios like technicians juggling jobs while waiting on parts.
- **Effective concurrency** at any time T:

```
effective_capacity(T) = min(free_capable_bays(T), available_technicians(T))
```

A slot is available only if `effective_capacity(T) ≥ 1`.

#### Separation of Concerns: Capacity Gating vs. Work Assignment

| Concern | When | What it answers |
|---|---|---|
| **Capacity Gating** | Scheduling time (front desk) | *"Does the shop have enough of both resources at this time?"* |
| **Work Assignment** | Before the scheduled date (manager) | *"Which specific technician does this job?"* |

Capacity gating does not require naming a specific technician. The system counts the technician pool to determine if a slot is feasible.

### 7.2 Technician Roster & Availability

#### Technician Roster

Technicians are identified by filtering the standard **Employee** DocType using a configurable designation:

- `designation` matches `Shop Settings → technician_designation` (default: `"Technician"`)
- `status = "Active"`

No dedicated "Shop Technician" DocType is needed. The designation filter is simple, admin-configurable, and works with any existing Employee records.

All technicians share the shop operating hours defined in Shop Settings (`operating_hours_start`, `operating_hours_end`, `break_start`, `break_end`). There are no per-technician shift schedules.

#### Leave-Aware Availability (HRMS Integration)

When `enable_technician_capacity` is on, the system queries HRMS **Leave Application** records to exclude technicians on approved leave from the available pool:

- Queries: `Leave Application` where `employee` is in technician roster, `status = "Approved"`, `from_date <= date <= to_date`, `docstatus = 1`.
- Full-day leave: technician excluded from pool entirely.
- Half-day leave (`half_day = 1`): technician counted as half-available (excluded from AM or PM window based on `half_day_date`).

#### Availability Formula

A technician is "available" at time T if:

```
is_active(employee)                                    # Employee.status = "Active"
AND matches_designation(employee)                      # designation = technician_designation
AND NOT on_approved_full_day_leave(employee, date)     # no approved Leave Application
AND NOT has_overlapping_schedule_entry(employee, T)    # no conflicting assignment
```

### 7.3 Lunch-Aware Time Windows

The `estimated_duration` on a Schedule Entry represents **pure work-minutes** (e.g., 120 minutes). When the scheduling layer calculates the **effective time window** a job occupies — for bay overlap checks, technician overlap checks, and timeline rendering — it accounts for the lunch break.

If a job's work window spans across the configured break, the break duration is added to the effective end time:

```python
def effective_end_time(start_time, duration_minutes, break_start=None, break_end=None):
    """
    Calculates the clock-time end of a job, inserting the lunch break if the job spans it.
    
    - start_time: job start time
    - duration_minutes: pure work-minutes (P80 estimate)
    - break_start, break_end: from Shop Settings (optional)
    
    If break is configured and the job's work window spans into the break:
      effective_end = naive_end + break_duration
    Otherwise:
      effective_end = naive_end
    """
    naive_end = start_time + duration_minutes
    
    if break_start and break_end:
        break_duration = break_end - break_start
        if start_time < break_start and naive_end > break_start:
            # Job spans into or through lunch → insert break
            return naive_end + break_duration
    
    return naive_end
```

**Examples** (assuming lunch 12:00–12:30):

| Start | Work Duration | Naive End | Effective End | Explanation |
|---|---|---|---|---|
| 08:00 | 120 min | 10:00 | 10:00 | Finishes before lunch — no adjustment |
| 11:00 | 120 min | 13:00 | 13:30 | Spans lunch — 30 min break inserted |
| 11:30 | 45 min | 12:15 | 12:45 | Spans into lunch — 30 min break inserted |
| 13:00 | 90 min | 14:30 | 14:30 | Starts after lunch — no adjustment |

All capacity APIs (`check_bay_availability`, `auto_assign_bay`, `get_available_slots`, technician overlap checks) use `effective_end_time()` for time window calculations. The `estimated_duration` stored on the Schedule Entry remains the pure work-minutes estimate — the lunch insertion is a scheduling-layer concern, not an estimation concern.

### 7.4 Capacity & Assignment APIs (`induct_shop/api/scheduling.py`)

#### Bay Capacity APIs

**`check_bay_availability(service_bay, date, start_time, duration_minutes, exclude_entry=None) → bool`**

- Queries existing Schedule Entries assigned to the given `service_bay` for the given date (status not `Cancelled`).
- Computes effective time windows using `effective_end_time()` (lunch-aware) for both the proposed entry and all existing entries.
- Checks if any existing entry's effective time window overlaps with the proposed window.
- Returns `True` if the bay is free, `False` if it conflicts.
- The `exclude_entry` parameter allows the current entry to be excluded during re-validation (e.g., when rescheduling or manager override).
- Used by Schedule Entry's `validate` hook to prevent double-booking a bay.

**`auto_assign_bay(date, start_time, duration_minutes, required_tags=None) → str`**

- Verifies the technician pool has capacity (if `enable_technician_capacity` is on). Raises `frappe.ValidationError` if all technicians are occupied.
- Queries all active Service Bays and filters to those whose equipment tags are a superset of `required_tags`.
- Evaluates capable bays using an earliest-fit strategy, selecting the first capable bay where the lunch-aware time window is completely free.
- Returns the assigned `bay_name`. Raises `frappe.ValidationError` if no capable bay is available.

**`get_available_bays(date, start_time, duration_minutes, required_tags=None) → list[dict]`**

- Queries all active Service Bays.
- Filters bays based on equipment tags: verifies each candidate bay provides all `required_tags` (set-superset check).
- For each matching bay, checks if the proposed lunch-aware time window is free.
- Returns a list of available bays with their equipment tags (e.g., `{"bay_name": "Bay 1", "equipment_tags": ["Lift"]}`).
- Used by managerial UI and capacity calculation services.

**`get_available_slots(date, duration_minutes, required_tags=None, service_bay=None) → list[dict]`**

- Loads operating hours and lunch break settings from Shop Settings.
- Walks through operating hours in `default_slot_interval` increments.
- Filters out any candidate slots that overlap with the configured lunch break window (no jobs start during lunch).
- For each remaining candidate slot, computes the lunch-aware effective end time.
- Checks **both** resource pools at each candidate slot:
  1. At least one capable bay is free during the effective time window.
  2. At least one technician is available (on duty, not on leave, no overlapping entry) during the window — if `enable_technician_capacity` is on.
- Returns enriched slot data:

```json
[
  {
    "start_time": "08:00",
    "available_bays": 3,
    "available_technicians": 2,
    "effective_capacity": 2,
    "bottleneck": "technicians"
  },
  {
    "start_time": "08:30",
    "available_bays": 2,
    "available_technicians": 2,
    "effective_capacity": 2,
    "bottleneck": null
  }
]
```

Slots where `effective_capacity < 1` are excluded from the response.

#### Technician Capacity APIs (`induct_shop/api/technician_availability.py`)

**`get_active_technicians(date=None) → list[dict]`**

- Returns all Employees where `designation` matches `Shop Settings → technician_designation` and `status = "Active"`.
- If `date` is provided, flags employees on approved leave for that date.
- Returns: `[{"employee": "EMP-001", "employee_name": "Alex Rivera", "on_leave": False, "half_day": False}, ...]`

**`get_technician_pool_availability(date, start_time, duration_minutes) → dict`**

The core pool-level capacity gating function:

- For each active technician: check leave status and count overlapping Schedule Entries during the proposed lunch-aware time window.
- Returns:

```json
{
  "total_technicians": 3,
  "on_leave": 1,
  "on_duty": 2,
  "occupied": 1,
  "available": 1,
  "is_available": true
}
```

- Used by `auto_assign_bay()`, `get_available_slots()`, and the Schedule Entry `validate` hook.

**`check_technician_availability(employee, date, start_time, duration_minutes, exclude_entry=None) → dict`**

Individual-level availability check for a specific technician:

- Returns:

```json
{
  "is_available": true,
  "reason": null,
  "on_leave": false,
  "half_day": false,
  "conflicts": []
}
```

- `reason` is `null` when available, or one of: `"on_leave"`, `"overlap"`, `"inactive"`.
- Used by Schedule Entry `validate` hook (soft warning) and the technician selector UI.

**`get_technician_queue(employee, date) → dict`**

Personal work queue for the Technician Daily View:

- Queries Schedule Entries where `assigned_technician = employee` and `scheduled_date = date`, status not `Cancelled`, ordered by `scheduled_time` ascending.
- Computes lunch-aware effective end times for each entry.
- Returns:

```json
{
  "employee": "EMP-001",
  "employee_name": "Alex Rivera",
  "on_leave": false,
  "entries": [
    {
      "name": "SE-00012",
      "scheduled_time": "08:00",
      "estimated_duration": 77,
      "effective_end_time": "09:17",
      "service_bay": "Bay 1",
      "customer": "Jane Smith",
      "repair_vehicle": "2021 Model Y",
      "items_summary": "Brake Pad Replacement",
      "status": "Scheduled",
      "sales_order": "SO-00042"
    }
  ],
  "total_jobs": 5,
  "total_minutes": 380,
  "utilization_pct": 79.2,
  "gaps": [
    {"after": "SE-00012", "duration_minutes": 15, "start": "09:17"}
  ]
}
```

- `utilization_pct` is calculated against shop operating minutes (minus lunch break).

**`get_daily_technician_overview(date) → dict`**

Shop-wide technician dashboard for managers:

```json
{
  "date": "2026-07-23",
  "operating_minutes": 480,
  "technicians": [
    {
      "employee": "EMP-001",
      "employee_name": "Alex Rivera",
      "on_leave": false,
      "job_count": 5,
      "total_minutes": 380,
      "utilization_pct": 79.2
    }
  ],
  "unassigned_entries": [
    {"name": "SE-00015", "scheduled_time": "14:00", "customer": "...", "repair_vehicle": "..."}
  ],
  "shop_summary": {
    "total_technicians": 3,
    "on_duty": 2,
    "on_leave": 1,
    "total_bays": 4,
    "bottleneck": "technicians",
    "total_scheduled_hours": 18.5,
    "unassigned_count": 1
  }
}
```

---

## 8. Shop Settings (Singleton DocType)

A singleton DocType to configure scheduling parameters:

| Field | Type | Description |
|---|---|---|
| `operating_hours_start` | Time | Shop opens (e.g., 08:00) |
| `operating_hours_end` | Time | Shop closes (e.g., 17:00) |
| `break_start` | Time | Start of shop break / lunch window (e.g., 12:00). Optional. |
| `break_end` | Time | End of shop break / lunch window (e.g., 12:30). Optional. |
| `default_slot_interval` | Int | Slot granularity in minutes (e.g., 30) for the scheduling UI |
| `holiday_list` | Link (Holiday List) | ERPNext Holiday List for days the shop is closed |
| `scheduling_horizon_days` | Int | How far ahead scheduling is allowed (e.g., 30 days) |
| `technician_designation` | Data | Employee designation used to identify technicians. Default: `"Technician"`. |
| `enable_technician_capacity` | Check | Master toggle for dual-resource capacity gating. Default: checked. When unchecked, reverts to bay-only capacity model for shops that don't need technician tracking. |

> [!NOTE]
> The `number_of_bays` field is no longer needed — bay count is derived dynamically from the number of active Service Bay records. Technician count is derived from active Employees matching the configured designation. Leave checking is always active when `enable_technician_capacity` is on, using standard HRMS Leave Application queries.

---

## 9. Staff-Facing UI

The UI is split into distinct views tailored to specific staff roles:

### 9.1 Schedule Service Dialog (Front Desk View)

Designed for rapid appointment creation without exposing shop layout complexity:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Schedule Service                                    SO-00042      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Date:  [◀ July 23, 2026 ▶]      Est. Duration: ██ 77 min (P80)   │
│                                                                     │
│  10 slots available · Bottleneck: Technicians (2 techs, 4 bays)    │
│                                                                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │  8:00  │ │  8:30  │ │  9:00  │ │  9:30  │ │ 10:00  │           │
│  │ 2 bays │ │ 2 bays │ │ 1 bay  │ │ 2 bays │ │ 2 bays │           │
│  │ 2 tech │ │ 2 tech │ │ 1 tech │ │ 2 tech │ │ 1 tech │           │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘           │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │ 10:30  │ │ 11:00  │ │ 13:00  │ │ 13:30  │ │ 14:00  │           │
│  │ 2 bays │ │ 1 bay  │ │ 2 bays │ │ 2 bays │ │ 2 bays │           │
│  │ 2 tech │ │ 1 tech │ │ 2 tech │ │ 2 tech │ │ 2 tech │           │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘           │
│                          (12:00–12:30 lunch break excluded)         │
│                                                                     │
│  Technician: [Alex Rivera          ▼]                               │
│              Alex Rivera · 3 jobs · 4h 30m · 56% utilized           │
│                                                                     │
│  Notes:      [                                         ]            │
│                                                                     │
│                                          [Cancel]  [Schedule]       │
└─────────────────────────────────────────────────────────────────────┘
```

- **Slot Selection**: Displays only open, available start time slots for the chosen date. Lunch break windows and fully-booked slots are excluded.
- **Dual-Resource Capacity Indicator**: Each slot shows available bays and technicians. The header summarizes the bottleneck.
- **Automated Bay Assignment**: Front desk staff selects date and time. The system automatically assigns a capable bay via `auto_assign_bay()`.
- **Technician Utilization Preview**: When a technician is selected, their current load for the chosen date is shown. Overlaps produce a yellow warning banner (non-blocking).

### 9.2 Calendar View (General View)

A Frappe calendar view for the Schedule Entry DocType (`doctype_calendar_js` hook):

- Renders Schedule Entries on a standard day/week calendar grid.
- Each block shows: customer name, vehicle, assigned bay, estimated duration, and status (color-coded).
- Job blocks that span the lunch break are rendered with a visual break indicator (gap in the block) to reflect the lunch-aware effective end time.
- Clicking a block navigates to the Schedule Entry form.

### 9.3 Shop Floor Dashboard (Manager View)

A per-bay day-strip timeline view designed for shop floor managers:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Shop Floor · July 23, 2026                           [◀ Today ▶]  │
│  3 of 4 bays active · 2 of 3 techs on duty (1 on leave)           │
│  Bottleneck: Technicians · 5 appointments · 1 unassigned           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  BAY LANES (08:00 ──────────────────────────────────────── 17:00)  │
│                              12:00  12:30                           │
│  Bay 1  ████ SO-42 ██████░░░░░░░░░░████ SO-44 ██████               │
│         Brake Pads    ░ lunch ░     Drive Unit                      │
│         Alex R.                     Alex R.                         │
│                                                                     │
│  Bay 2  ░░░░░░░░░░░░░████ SO-45 ██████████████░░░░░░░░░░░          │
│                       Suspension Insp.                              │
│                       Jordan M.                                     │
│                                                                     │
│  Bay 3  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████ SO-47 ████       │
│                                              12V Battery            │
│                                              ⚠ unassigned           │
│                                                                     │
│  Bay 4  (inactive)                                                  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  TECHNICIAN LOAD                                                    │
│                                                                     │
│  Alex R.       ████████░░  79%  · 4 jobs                           │
│  Jordan M.     ██████░░░░  58%  · 3 jobs                           │
│  Sam K.        ░░░░░░░░░░  ON LEAVE                                │
│                                                                     │
│  ⚠ 1 unassigned entry (14:00, Bay 3)                               │
└─────────────────────────────────────────────────────────────────────┘
```

- **Horizontal Swim Lanes**: Renders active Service Bays on the Y-axis and shop operating hours on the X-axis.
- **Capacity Summary Header**: Displays dual-resource metrics including bottleneck indicator, on-duty/on-leave technician counts, and unassigned entry count.
- **Lunch Break Visualization**: The lunch window is rendered as a distinct hatched/shaded column across all bay lanes. Jobs that span lunch show a visual gap with the effective end time shifted accordingly.
- **Visual Block Status**: Color-coded blocks for `Scheduled` (blue), `In Progress` (amber), `Needs Review` (red), `Completed` (green).
- **Manual Bay Reassignment**: Managers can view bay allocations and manually edit `service_bay` on the Schedule Entry form when necessary. The backend `validate` controller re-verifies bay availability on save to prevent accidental double-booking.
- **Technician Load Panel**: A collapsible bottom section showing each technician's utilization bar for the day. Each bar shows: technician name, job count, utilization percentage, and a visual fill indicator. Technicians on leave are shown with a distinct "ON LEAVE" label. Clicking a technician's bar navigates to their Technician Daily View.
- **Unassigned Entries Alert**: Schedule Entries for the day without an `assigned_technician` are highlighted in the Technician Load Panel so managers can spot assignment gaps.

### 9.4 List View

List view customization with:
- Status-based color indicators.
- Quick filters: by date, by status, by bay, by technician.

### 9.5 Technician Daily View

A dedicated page providing each technician with a personal, read-optimized timeline of their day:

```
┌─────────────────────────────────────────────────────────────────────┐
│  Technician Daily View              Date: [◀ July 23, 2026 ▶]     │
│  [Technician Selector ▼]   (defaults to logged-in employee)        │
├─────────────────────────────────────────────────────────────────────┤
│  DAILY SUMMARY                                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                   │
│  │ 4 Jobs │  │ 6h 20m │  │ Bay 1  │  │ 79%    │                   │
│  │ Today  │  │ Total  │  │ Primary│  │ Util.  │                   │
│  └────────┘  └────────┘  └────────┘  └────────┘                   │
├─────────────────────────────────────────────────────────────────────┤
│  TIMELINE (08:00 – 17:00)                                           │
│                                                                     │
│  08:00 ─┬─ ● 2021 Model Y — Brake Pad Replacement ──────── 77min  │
│         │   Bay 1 · SO-00042 · Scheduled                           │
│         │                                                           │
│  09:17 ─┼─ ○ 28min gap                                             │
│         │                                                           │
│  09:45 ─┼─ ● 2023 Model 3 — Drive Unit Service ─────────── 95min  │
│         │   Bay 1 · SO-00044 · Scheduled                           │
│         │                                                           │
│  11:20 ─┼─ ○ 40min gap                                             │
│         │                                                           │
│  12:00 ─┼─ ░░░ Lunch Break ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 30min   │
│         │                                                           │
│  12:30 ─┼─ ● 2022 Model X — Suspension Inspection ──────── 65min  │
│         │   Bay 2 · SO-00045 · Scheduled                           │
│         │                                                           │
│  13:35 ─┼─ ○ 25min gap                                             │
│         │                                                           │
│  14:00 ─┼─ ● 2024 Cybertruck — 12V Battery Replacement ── 45min   │
│         │   Bay 1 · SO-00047 · Scheduled                           │
│         │                                                           │
│  14:45 ─┴─ Day ends at 17:00 (2h 15m remaining capacity)           │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│  NEXT UP: 2021 Model Y — Brake Pad Replacement (08:00, Bay 1)      │
│  [View Schedule Entry]   [Start Job]                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Key behaviors**:

- **Auto-selects the logged-in user's linked Employee** (via `frappe.db.get_value("Employee", {"user_id": frappe.session.user})`). Managers can switch to any technician via the selector dropdown.
- The **"Next Up"** bar highlights the next non-completed, non-cancelled entry based on current time. This answers the single most important question: "what should I be doing?"
- Clicking any timeline entry navigates to the Schedule Entry form.
- **"Start Job"** button transitions the highlighted Schedule Entry's status from `Scheduled` → `In Progress` (convenience action).
- Gaps between jobs are surfaced explicitly so technicians and managers can see idle windows.
- The lunch break window (from Shop Settings) is rendered as a distinct block in the timeline.
- Jobs that span the lunch break show the lunch as an inserted pause — the work resumes after lunch with the remaining duration, and the effective end time reflects this.

---

## 10. Source Files

| File | Purpose |
|---|---|
| `induct_shop/scheduling/estimation_light.py` | Pure-Python log-normal estimator — `estimate_duration`, `estimate_total_duration` |
| `induct_shop/api/estimation_service.py` | Frappe integration service exposing `get_estimate` and `get_total_estimate` |
| `induct_shop/api/scheduling.py` | Bay capacity & assignment APIs — `check_bay_availability`, `auto_assign_bay`, `get_available_bays`, `get_available_slots`, `effective_end_time` |
| `induct_shop/api/technician_availability.py` | Technician roster & capacity APIs — `get_active_technicians`, `get_technician_pool_availability`, `check_technician_availability`, `get_technician_queue`, `get_daily_technician_overview` |
| `induct_shop/induct_shop/doctype/service_bay/` | Service Bay DocType (JSON schema + Python controller) |
| `induct_shop/induct_shop/doctype/schedule_entry/` | Schedule Entry DocType (JSON schema + Python controller) |
| `induct_shop/induct_shop/doctype/shop_settings/` | Shop Settings singleton DocType |
| `induct_shop/public/js/sales_order.js` | Client script adding "Schedule Service" slot picker button to Sales Order |
| `induct_shop/public/js/schedule_entry_calendar.js` | Calendar view for Schedule Entry |
| `induct_shop/public/js/schedule_entry_list.js` | List view customization for Schedule Entry |
| `induct_shop/induct_shop/page/shop_floor/` | Shop Floor Dashboard page — bay lanes + technician load panel |
| `induct_shop/induct_shop/page/technician_daily/` | Technician Daily View page — personal timeline + "Next Up" |

---

## 11. Dependencies

| Dependency | Required | Purpose |
|---|---|---|
| ERPNext | Yes | Sales Order, Project, Customer, Item, Holiday List |
| HRMS | Yes | Leave Application (technician leave-aware capacity) |
