---
type: Specification
title: "Scheduling System"
description: "Comprehensive specification for the Induct Shop scheduling system, covering FRT-based lightweight estimation, Sales Order-driven scheduling, per-bay capacity management, and staff-facing UI."
status: Proposed
tags: [system, scheduling, estimation, specification, log-normal, capacity]
timestamp: 2026-07-20T22:38:00Z
---

# Scheduling System

The scheduling system provides duration estimation for automotive repair operations and manages shop capacity to prevent overbooking. It is built in three layers: a **pure-Python estimation engine**, a **Frappe integration layer** that exposes estimates through the existing ERPNext workflow, and a **scheduling layer** that generates and manages Schedule Entries from confirmed Sales Orders.

> [!NOTE]
> This specification describes a **Lightweight FRT-Based Estimator (Phase 1)** paired with a **per-bay capacity model**. Customer-facing appointment booking is deferred to a future customer portal integration — this system focuses exclusively on backend logic and the staff-facing UI.

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
│          service_bay (required), assigned_technician (advisory),     │
│          status                                                     │
│  Duration: auto-calculated via estimation_service.get_total_estimate│
└────────────────────────┬────────────────────────────────────────────┘
                         │ validated against
┌────────────────────────▼────────────────────────────────────────────┐
│                   Capacity Management Layer                         │
│                                                                     │
│  Service Bay DocType → per-bay identity with capability flags       │
│  Per-bay overlap check → no two entries in the same bay at once     │
│  Shop Settings → operating hours, holidays, slot interval           │
│  Slot availability API → returns open bays per time window          │
└─────────────────────────────────────────────────────────────────────┘
                         │ surfaced via
┌────────────────────────▼────────────────────────────────────────────┐
│                   Staff-Facing UI                                    │
│                                                                     │
│  Calendar view → day/week schedule with color-coded statuses        │
│  List view → filterable, sortable schedule list                     │
│  Sales Order button → "Schedule Service" dialog                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Decoupled engine** — The estimation math has zero Frappe dependencies. It can be unit-tested and reasoned about in isolation.
2. **Sales Order as the source of truth** — The Sales Order is a confirmation of service that contains all necessary services and parts. Schedule Entries are always generated from a submitted Sales Order.
3. **Per-bay capacity model** — Each Schedule Entry is assigned to a specific Service Bay. Overbooking prevention ensures no two entries overlap on the same bay. Bays have capability flags (e.g., `has_lift`) so staff can match jobs to appropriate bays.
4. **1:1 relationship** — Each Sales Order maps to exactly one Schedule Entry. Follow-up visits require a new Sales Order.
5. **P80 as the scheduling block** — The log-normal P80 estimate provides a conservative built-in buffer. No additional buffer is applied on top.

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
| `estimated_duration` | Duration | Auto-calculated P80 estimate from all service items on the SO. Minutes. |
| `service_bay` | Link (Service Bay) | The specific bay this job is assigned to. **Required.** Drives capacity checks. |
| `assigned_technician` | Link (Employee) | Technician assignment. **Optional and advisory** — does not block scheduling. |
| `status` | Select | `Draft` → `Scheduled` → `Needs Review` → `In Progress` → `Completed` → `Cancelled` |
| `notes` | Small Text | Free-text notes for the service advisor. |
| `items_summary` | Long Text | Read-only auto-generated summary of service items from the SO. |

### 5.2 Controller Logic

- **`before_insert`**: Auto-fetch `project`, `customer`, `repair_vehicle` from the Sales Order and its linked Project.
- **`before_insert`**: Auto-calculate `estimated_duration` by calling `get_total_estimate()` with all service item codes from the linked Sales Order.
- **`validate`**: Call `check_bay_availability()` to verify the assigned bay is free for the chosen date/time/duration window. Raise `frappe.ValidationError` if the bay is already occupied.

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
  - **Optional Technician Link & Notes** fields.
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

### 7.1 Model: Per-Bay Capacity

The system uses a **per-bay capacity model**: each Schedule Entry is assigned to a specific Service Bay, and the system ensures no two Schedule Entries overlap on the same bay.

- Each Schedule Entry occupies its assigned bay for the full `estimated_duration` window (`scheduled_time` to `scheduled_time + estimated_duration`).
- Two Schedule Entries on the **same bay** cannot overlap in time. If they would, the system rejects the later one.
- Different bays provide different equipment tags (e.g., "Lift", "Alignment Rack"). Staff selects an appropriate bay for the job, and the system filters available bays by ensuring the bay's tag set is a superset of the service's equipment requirements.
- Technician assignment remains advisory and does not affect capacity calculations.

### 7.2 Capacity & Assignment APIs (`induct_shop/api/scheduling.py`)

**`check_bay_availability(service_bay, date, start_time, duration_minutes, exclude_entry=None) → bool`**

- Queries existing Schedule Entries assigned to the given `service_bay` for the given date (status not `Cancelled`).
- Checks if any existing entry's time window overlaps with the proposed `[start_time, start_time + duration]` window.
- Returns `True` if the bay is free, `False` if it conflicts.
- The `exclude_entry` parameter allows the current entry to be excluded during re-validation (e.g., when rescheduling or manager override).
- Used by Schedule Entry's `validate` hook to prevent double-booking a bay.

**`auto_assign_bay(date, start_time, duration_minutes, required_tags=None) → str`**

- Automatically selects an appropriate Service Bay for a job without front desk staff intervention.
- Queries all active Service Bays and filters to those whose equipment tags are a superset of `required_tags`.
- Evaluates capable bays using an earliest-fit strategy, selecting the first capable bay where `[start_time, start_time + duration]` is completely free.
- Returns the assigned `bay_name`. Raises `frappe.ValidationError` if no capable bay is available.

**`get_available_bays(date, start_time, duration_minutes, required_tags=None) → list[dict]`**

- Queries all active Service Bays.
- Filters bays based on equipment tags: verifies each candidate bay provides all `required_tags` (set-superset check).
- For each matching bay, checks if the proposed time window is free.
- Returns a list of available bays with their equipment tags (e.g., `{"bay_name": "Bay 1", "equipment_tags": ["Lift"]}`).
- Used by managerial UI and capacity calculation services.

**`get_available_slots(date, duration_minutes, required_tags=None, service_bay=None) → list[dict]`**

- Loads operating hours and lunch break settings (`break_start`, `break_end`) from Shop Settings.
- Walks through operating hours in `default_slot_interval` increments.
- Filters out any candidate slots that overlap with the configured lunch break window.
- If `required_tags` is provided, ensures at least one active bay offering those equipment tags is free during the slot window.
- Returns a list of available start times `[{"start_time": "08:00"}, {"start_time": "08:30"}, ...]`. Unavailable slots are excluded.

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

> [!NOTE]
> The `number_of_bays` field is no longer needed — bay count is derived dynamically from the number of active Service Bay records. The P80 estimate provides a conservative buffer; no additional explicit buffer between appointments is applied.

---

## 9. Staff-Facing UI

The UI is split into distinct views tailored to specific staff roles:

### 9.1 Schedule Service Dialog (Front Desk View)

Designed for rapid appointment creation without exposing shop layout complexity:

- **Slot Selection**: Displays only open, available start time slots for the chosen date. Unavailable slots and lunch breaks are excluded automatically.
- **Automated Bay Assignment**: Front desk staff selects date and time. The system automatically assigns a capable bay via `auto_assign_bay()`.
- **Capacity Indicator**: High-level summary text (e.g., "10 slots available on July 23").

### 9.2 Calendar View (General View)

A Frappe calendar view for the Schedule Entry DocType (`doctype_calendar_js` hook):

- Renders Schedule Entries on a standard day/week calendar grid.
- Each block shows: customer name, vehicle, assigned bay, estimated duration, and status (color-coded).
- Clicking a block navigates to the Schedule Entry form.

### 9.3 Shop Floor Dashboard (Manager View)

A per-bay day-strip timeline view designed for shop floor managers:

- **Horizontal Swim Lanes**: Renders active Service Bays on the Y-axis and shop operating hours on the X-axis.
- **Capacity Summary Header**: Displays shop-wide metrics (e.g., "3 of 4 bays active · 6h 30min free capacity · 5 appointments").
- **Visual Block Status**: Color-coded blocks for `Scheduled` (blue), `In Progress` (amber), `Needs Review` (red), `Completed` (green).
- **Manual Bay Reassignment**: Managers can view bay allocations and manually edit `service_bay` on the Schedule Entry form when necessary. The backend `validate` controller re-verifies bay availability on save to prevent accidental double-booking.

### 9.4 List View

List view customization with:
- Status-based color indicators.
- Quick filters: by date, by status, by bay, by technician.

---

## 10. Source Files

| File | Purpose |
|---|---|
| `induct_shop/scheduling/estimation_light.py` | Pure-Python log-normal estimator — `estimate_duration`, `estimate_total_duration` |
| `induct_shop/api/estimation_service.py` | Frappe integration service exposing `get_estimate` and `get_total_estimate` |
| `induct_shop/api/scheduling.py` | Capacity & bay assignment APIs — `check_bay_availability`, `auto_assign_bay`, `get_available_bays`, `get_available_slots` |
| `induct_shop/induct_shop/doctype/service_bay/` | Service Bay DocType (JSON schema + Python controller) |
| `induct_shop/induct_shop/doctype/schedule_entry/` | Schedule Entry DocType (JSON schema + Python controller) |
| `induct_shop/induct_shop/doctype/shop_settings/` | Shop Settings singleton DocType |
| `induct_shop/public/js/sales_order.js` | Client script adding "Schedule Service" slot picker button to Sales Order |
| `induct_shop/public/js/schedule_entry_calendar.js` | Calendar view for Schedule Entry |
| `induct_shop/public/js/schedule_entry_list.js` | List view customization for Schedule Entry |
| `induct_shop/induct_shop/page/shop_floor/` | Shop Floor Dashboard page for floor managers |
