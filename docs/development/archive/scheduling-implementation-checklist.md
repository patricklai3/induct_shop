---
type: Specification
title: "Scheduling System – Staged Implementation Checklist"
description: "Progressive build-and-verify checklist for the scheduling system. Each stage must pass its acceptance criteria before proceeding to the next. For full specification details, see scheduling-system.md."
status: Archived
tags: [scheduling, implementation, checklist, staged, archived]
timestamp: 2026-08-03T20:59:18Z
references:
  - docs/systems/scheduling-system.md
---

# Scheduling System – Staged Implementation Checklist

> [!IMPORTANT]
> This is a **build-and-verify** checklist. Complete and test each stage before starting the next. For detailed schemas, API signatures, and behavioral requirements, refer to [scheduling-system.md](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/systems/scheduling-system.md).

> [!NOTE]
> All DocTypes must be **Standard DocTypes** (`custom=0`) with JSON schemas and Python controllers exported to the codebase. Custom fields on existing DocTypes must be declared in `hooks.py` (via `custom_fields` or `fixtures`) and queries must defensively check column existence with `frappe.db.has_column()`.

---

## Stage 1 — Estimation Engine (Pure Python)

**Goal**: Implement the log-normal estimation math with zero Frappe dependencies.

**Spec Reference**: §2 (Estimation Engine)

**Files**: `induct_shop/scheduling/estimation_light.py`

- [x] Implement `estimate_duration(flat_rate_minutes, sigma=0.30)` → returns P80 in minutes (integer, rounded up)
- [x] Implement `estimate_total_duration(flat_rate_list, sigma=0.30)` → Fenton-Wilkinson multi-operation summation, returns total P80 in minutes
- [x] Handle edge cases: empty list returns 0, single-item list bypasses summation, zero/negative FRT raises ValueError

### Stage 1 — Acceptance Criteria

- [x] **Unit tests pass** — pure-Python tests (no Frappe test runner needed) covering:
  - Single FRT: 60 min → ~77 min P80
  - Multi-FRT summation produces a tighter total than naively summing individual P80s
  - Edge cases (empty list, single item, zero FRT)
- [x] Module is importable independently (`python -c "from induct_shop.scheduling.estimation_light import estimate_duration"`)

---

## Stage 2 — Estimation Service (Frappe Integration)

**Goal**: Wrap the estimation engine with Frappe data access (Item → `custom_frt` lookup).

**Spec Reference**: §3 (Frappe Integration Layer)

**Files**: `induct_shop/api/estimation_service.py`

- [x] Implement `get_estimate(item_code, **kwargs)` — fetches `custom_frt` from Item, calls `estimate_duration()`, returns P80
- [x] Implement `get_total_estimate(item_codes, **kwargs)` — fetches FRT for all items, calls `estimate_total_duration()`, returns total P80
- [x] Defensive check: `frappe.db.has_column("Item", "custom_frt")` before querying `custom_frt`
- [x] Graceful handling of missing FRT: items with no `custom_frt` are skipped (or use a configurable fallback)
- [x] Expose as whitelisted methods if needed for client-side calls

### Stage 2 — Acceptance Criteria

- [x] **Frappe test** — call `get_estimate()` with a known item code that has `custom_frt` set and verify the returned P80
- [x] **Frappe test** — call `get_total_estimate()` with multiple item codes and verify summation result
- [x] **Defensive check test** — verify no crash when `custom_frt` column doesn't exist

---

## Stage 3 — Foundation DocTypes (Shop Settings + Service Bay)

**Goal**: Create the configuration and physical-resource DocTypes that the scheduling layer depends on.

**Spec Reference**: §4 (Service Bay), §8 (Shop Settings)

**Files**:
- `induct_shop/induct_shop/doctype/shop_settings/` (singleton)
- `induct_shop/induct_shop/doctype/service_bay/`
- `induct_shop/induct_shop/doctype/service_bay_equipment/` (child table)

### Shop Settings (Singleton)

- [x] Create singleton DocType with fields: `operating_hours_start`, `operating_hours_end`, `break_start`, `break_end`, `default_slot_interval`, `holiday_list`, `scheduling_horizon_days`, `technician_designation`, `enable_technician_capacity`
- [x] Set sensible defaults (see §8 for values)

### Service Bay + Equipment Tags

- [x] Create Service Bay DocType with fields: `bay_name` (naming/title field), `equipment` (child table), `is_active`, `description`
- [x] Create `Service Bay Equipment` child table DocType with an equipment tag field
- [x] Verify `bay_name` is the naming field and title field

### Stage 3 — Acceptance Criteria

- [x] `bench migrate` succeeds without errors
- [x] Shop Settings singleton can be created and saved via the UI
- [x] Multiple Service Bays can be created with different equipment tags
- [x] Filtering `Service Bay` by `is_active` works correctly
- [x] **Reinstall test** — `bench reinstall` (or install on fresh site) creates both DocTypes without manual intervention

---

## Stage 4 — Schedule Entry DocType (Schema Only)

**Goal**: Create the Schedule Entry DocType with its schema and basic controller hooks, **without** capacity validation logic (that comes in Stage 5).

**Spec Reference**: §5 (Schedule Entry DocType)

**Files**: `induct_shop/induct_shop/doctype/schedule_entry/`

- [x] Create Schedule Entry DocType with all fields per §5.1 schema
- [x] Enforce unique constraint on `sales_order` (1:1 relationship)
- [x] `before_insert`: auto-fetch `project`, `customer`, `repair_vehicle` from the linked Sales Order and its Project
- [x] `before_insert`: auto-calculate `estimated_duration` by calling `get_total_estimate()` with all service item codes from the SO
- [x] `items_summary` auto-generated from SO items
- [x] Status field with the workflow: `Draft` → `Scheduled` → `Needs Review` → `In Progress` → `Completed` → `Cancelled`

### Stage 4 — Acceptance Criteria

- [x] Can create a Schedule Entry linked to a submitted Sales Order — `project`, `customer`, `repair_vehicle`, `estimated_duration`, and `items_summary` auto-populate correctly
- [x] Attempting to create a second Schedule Entry for the same Sales Order is blocked (unique constraint)
- [x] `estimated_duration` value matches the expected P80 for the SO's service items
- [x] Status transitions work (manual changes for now)
- [x] `bench migrate` succeeds; DocType survives reinstall

---

## Stage 5 — Bay Capacity APIs + Lunch-Aware Time Windows

**Goal**: Implement the bay-side capacity logic including lunch-aware effective end time calculation.

**Spec Reference**: §7.1 (bay constraint), §7.3 (Lunch-Aware Time Windows), §7.4 (Bay Capacity APIs)

**Files**: `induct_shop/api/scheduling.py`

- [x] Implement `effective_end_time(start_time, duration_minutes, break_start, break_end)` per §7.3
- [x] Implement `check_bay_availability(service_bay, date, start_time, duration_minutes, exclude_entry)` → returns `True`/`False`
- [x] Implement `auto_assign_bay(date, start_time, duration_minutes, required_tags)` → returns `bay_name` or raises ValidationError (technician pool check deferred to Stage 6)
- [x] Implement `get_available_bays(date, start_time, duration_minutes, required_tags)` → list of available bays with equipment tags
- [x] Implement `get_available_slots(date, duration_minutes, required_tags, service_bay)` → list of enriched slot dicts (bay data only for now; technician fields can be stubbed)
- [x] Wire `check_bay_availability()` into Schedule Entry's `validate` hook — raise `frappe.ValidationError` on bay overlap

### Stage 5 — Acceptance Criteria

- [x] **Lunch-aware time tests**:
  - Job ending before lunch → no adjustment
  - Job spanning lunch → break duration added to effective end
  - Job starting after lunch → no adjustment
- [x] **Bay overlap tests**:
  - Two entries on the same bay at the same time → blocked
  - Two entries on the same bay at non-overlapping times → allowed
  - Two entries on different bays at the same time → allowed
  - Rescheduling an existing entry (exclude_entry) → does not conflict with itself
- [x] **Auto-assign tests**:
  - Assigns first available capable bay
  - Raises error when no capable bays are available
  - Equipment tag filtering works (bay without required tag is skipped)
- [x] **Available slots**:
  - Slots during lunch break are excluded
  - Fully booked slots are excluded
  - Returned slot data includes `available_bays` count
- [x] Schedule Entry `validate` rejects save on bay conflict

---


## Stage 6 — Technician Capacity APIs

**Goal**: Implement technician roster management, leave-aware availability, and pool-level capacity gating.

**Spec Reference**: §7.2 (Technician Roster & Availability), §7.4 (Technician Capacity APIs)

**Files**: `induct_shop/api/technician_availability.py`

- [x] Implement `get_active_technicians(date)` — Employee designation filter + leave flagging
- [x] Implement `get_technician_pool_availability(date, start_time, duration_minutes)` — pool-level gating (counts total, on-leave, on-duty, occupied, available)
- [x] Implement `check_technician_availability(employee, date, start_time, duration_minutes, exclude_entry)` — individual overlap + leave check
- [x] Implement `get_technician_queue(employee, date)` — personal work queue with utilization
- [x] Implement `get_daily_technician_overview(date)` — shop-wide technician dashboard data
- [x] Wire technician pool gating into `auto_assign_bay()` (from Stage 5) when `enable_technician_capacity` is on
- [x] Wire technician pool check into Schedule Entry `validate` hook (hard block when pool is exhausted)
- [x] Wire individual technician check into Schedule Entry `validate` hook (soft warning on overlap/leave)
- [x] Update `get_available_slots()` to include technician availability data in returned slots (`available_technicians`, `effective_capacity`, `bottleneck`)

### Stage 6 — Acceptance Criteria

- [x] **Roster test** — only employees with matching designation and `Active` status are returned
- [x] **Leave integration test** — employee with approved Leave Application for a date is flagged as on-leave; half-day leave correctly handled
- [x] **Pool gating test**:
  - With 2 technicians on duty and 2 already occupied at time T → pool exhausted, slot unavailable
  - With `enable_technician_capacity` unchecked → technician checks are skipped entirely
- [x] **Individual overlap test** — assigning a technician who already has an overlapping Schedule Entry produces a soft warning (not a hard block)
- [x] **Dual-resource slots** — `get_available_slots()` returns correct `effective_capacity = min(free_bays, available_techs)` and identifies the bottleneck
- [x] **Work queue test** — `get_technician_queue()` returns entries in chronological order with utilization percentage
- [x] Schedule Entry `validate` with `enable_technician_capacity=1` blocks save when tech pool is exhausted

---


## Stage 7 — Sales Order Integration

**Goal**: Add the "Schedule Service" button and amendment handling to the Sales Order form.

**Spec Reference**: §6 (Sales Order Integration)

**Files**:
- `induct_shop/public/js/sales_order.js`
- `hooks.py` (add `doctype_js` and `doc_events` entries)

### Schedule Service Button

- [x] Add client script via `doctype_js` hook
- [x] Button appears only when SO is submitted (`docstatus == 1`) and no Schedule Entry exists for it
- [x] On click, opens the Schedule Service dialog (basic version — full UI polish in Stage 8):
  - Date picker (defaults to today or next business day)
  - Estimated duration badge (calls `get_total_estimate()`)
  - Available slots display (calls `get_available_slots()`)
  - Optional technician selector
  - Notes field
- [x] On submit: calls `auto_assign_bay()`, creates Schedule Entry, navigates to it
- [x] Button hidden after a Schedule Entry is created

### Amendment Handling

- [x] `doc_events` hook on Sales Order `on_submit` — when the SO is an amendment, update linked Schedule Entry status to `Needs Review`
- [x] Recalculate `estimated_duration` on the Schedule Entry from amended SO items
- [x] If new duration causes bay overlap, add a comment to the Schedule Entry alerting staff

### Stage 7 — Acceptance Criteria

- [x] Button visible on submitted SO, hidden otherwise
- [x] Button hidden when a Schedule Entry already exists for the SO
- [x] Full round-trip: click button → select date/slot → Schedule Entry created with correct bay, duration, SO link
- [x] Amendment flow: amend SO → linked Schedule Entry status changes to `Needs Review`, duration recalculated
- [x] Amendment overlap detection adds a comment when applicable
- [x] `hooks.py` entries survive `bench migrate`

---

## Stage 8 — Staff-Facing UI: Schedule Service Dialog (Polish)

**Goal**: Upgrade the basic dialog from Stage 7 into the full slot-picker UI per the specification wireframe.

**Spec Reference**: §9.1 (Schedule Service Dialog)

**Files**: `induct_shop/public/js/sales_order.js` (extend dialog)

- [x] Slot grid with clickable time slot buttons showing per-slot `available_bays` and `available_technicians`
- [x] Dual-resource capacity indicator in the header (slot count + bottleneck text)
- [x] Lunch break slots excluded; label showing the excluded window
- [x] Date navigation (prev/next day arrows)
- [x] Technician utilization preview when a technician is selected (name, job count, total time, utilization %)
- [x] Yellow warning banner when selected technician has an overlap at the chosen slot
- [x] Holiday awareness — no slots shown on holidays (from Shop Settings → Holiday List)
- [x] Auto-detect required equipment tags from SO items and pass to `get_available_slots()` / `auto_assign_bay()` — deferred from Stage 7

### Stage 8 — Acceptance Criteria

- [x] Visual match with the wireframe in §9.1
- [x] Slot grid updates dynamically when date is changed
- [x] Selecting a slot + submitting creates a valid Schedule Entry (end-to-end)
- [x] Technician utilization preview displays correct data
- [x] Overlap warning appears for conflicting technician assignment
- [x] No slots rendered during lunch window or on holidays

---

## Stage 9 — Staff-Facing UI: Calendar & List Views

**Goal**: Add Calendar and List view customizations for the Schedule Entry DocType.

**Spec Reference**: §9.2 (Calendar View), §9.4 (List View)

**Files**:
- `induct_shop/public/js/schedule_entry_calendar.js`
- `induct_shop/public/js/schedule_entry_list.js`
- `hooks.py` (add `doctype_calendar_js` hook)

- [x] Calendar view renders entries on day/week grid with customer, vehicle, bay, duration, and status
- [x] Color-coded status blocks (Scheduled=blue, In Progress=amber, Needs Review=red, Completed=green, Cancelled=grey)
- [x] Jobs spanning lunch show a visual break indicator
- [x] Clicking a block navigates to the Schedule Entry form
- [x] List view with status-based color indicators
- [x] List view quick filters: date, status, bay, technician

### Stage 9 — Acceptance Criteria

- [x] Calendar view renders at least one Schedule Entry correctly with color coding
- [x] Lunch break visual indicator appears for spanning jobs
- [x] List view filters produce correct results
- [x] Both views survive `bench build` and page reload

---

## Stage 10 — [Deferred] Staff-Facing UI: Shop Floor Dashboard

> [!NOTE]
> **Pushed to Future Unified Front-End Phase**: Implementation of the custom Shop Floor Dashboard page is stashed in [Shop Floor Dashboard UI](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/ui/shop-floor-dashboard.md). All underlying backend APIs (`get_daily_technician_overview()`) are ready.

**Spec Reference**: [Shop Floor Dashboard UI Specification](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/ui/shop-floor-dashboard.md)

**Stashed Files**: `induct_shop/induct_shop/page/shop_floor/`

- [ ] *(Deferred)* Create Frappe page with bay swim lanes (Y-axis = bays, X-axis = operating hours)
- [ ] *(Deferred)* Render Schedule Entry blocks on correct bay lanes with customer, vehicle, technician, status color
- [ ] *(Deferred)* Lunch break column rendered as hatched/shaded across all lanes
- [ ] *(Deferred)* Jobs spanning lunch show a visual gap with shifted effective end time
- [ ] *(Deferred)* Capacity summary header: active bays, on-duty/on-leave techs, bottleneck indicator, unassigned count
- [ ] *(Deferred)* Date navigation (prev/next day)
- [ ] *(Deferred)* Technician load panel (collapsible bottom section): per-technician utilization bar, job count, ON LEAVE label
- [ ] *(Deferred)* Unassigned entries highlighted in the technician panel
- [ ] *(Deferred)* Clicking a job block navigates to the Schedule Entry form
- [ ] *(Deferred)* Clicking a technician bar navigates to the Technician Daily View

---

## Stage 11 — [Deferred] Staff-Facing UI: Technician Daily View

> [!NOTE]
> **Pushed to Future Unified Front-End Phase**: Implementation of the custom Technician Daily View page is stashed in [Technician Daily View UI](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/ui/technician-daily-view.md). All underlying backend APIs (`get_technician_queue()`) are ready.

**Spec Reference**: [Technician Daily View UI Specification](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/ui/technician-daily-view.md)

**Stashed Files**: `induct_shop/induct_shop/page/technician_daily/`

- [ ] *(Deferred)* Create Frappe page with technician selector dropdown (defaults to logged-in employee)
- [ ] *(Deferred)* Daily summary cards: job count, total time, primary bay, utilization %
- [ ] *(Deferred)* Vertical timeline rendering: entries in chronological order with duration, bay, SO link, status
- [ ] *(Deferred)* Gaps between jobs rendered explicitly with duration
- [ ] *(Deferred)* Lunch break rendered as a distinct block in the timeline
- [ ] *(Deferred)* Jobs spanning lunch show inserted pause with remaining duration after
- [ ] *(Deferred)* "Next Up" bar highlighting the next non-completed/non-cancelled entry based on current time
- [ ] *(Deferred)* "View Schedule Entry" button on Next Up → navigates to form
- [ ] *(Deferred)* "Start Job" button on Next Up → transitions status `Scheduled` → `In Progress`
- [ ] *(Deferred)* Date navigation (prev/next day)

---

## Stage 12 — Integration Testing & Edge Cases

**Goal**: End-to-end verification of backend core, API layers, Sales Order dialog, and standard Frappe calendar/list views.

**Spec Reference**: All sections

- [x] **Full workflow test**: Create Sales Order with services → Submit → Schedule Service → verify Schedule Entry with correct duration, bay, and all fetched fields
- [x] **Capacity limits**: Fill all bays and/or exhaust technician pool → verify scheduling is correctly blocked
- [x] **Amendment flow**: Amend a scheduled Sales Order → verify `Needs Review` status and duration recalculation
- [x] **Leave integration**: Put a technician on leave → verify they are excluded from pool and their work queue reflects it
- [x] **Holiday handling**: Attempt to schedule on a holiday → verify no slots are available
- [x] **Lunch edge cases**: Schedule jobs that start before, during, and after lunch → verify effective end times are correct across all views
- [x] **Equipment tag filtering**: Require a tag (e.g., "Lift") → verify only bays with that tag are considered
- [x] **`enable_technician_capacity` toggle**: Turn off → verify system operates in bay-only mode without errors
- [x] **Reinstall resilience**: `bench reinstall` + `bench migrate` → all DocTypes, settings, and hooks intact
- [x] **Multi-day scheduling**: Verify scheduling across different dates doesn't cross-contaminate capacity checks

---

## Dependency Map

```mermaid
graph TD
    S1["Stage 1: Estimation Engine"]
    S2["Stage 2: Estimation Service"]
    S3["Stage 3: Shop Settings + Service Bay"]
    S4["Stage 4: Schedule Entry DocType"]
    S5["Stage 5: Bay Capacity APIs"]
    S6["Stage 6: Technician Capacity APIs"]
    S7["Stage 7: Sales Order Integration"]
    S8["Stage 8: Schedule Dialog Polish"]
    S9["Stage 9: Calendar & List Views"]
    S10["Stage 10: Shop Floor Dashboard (Deferred to UI Phase)"]
    S11["Stage 11: Technician Daily View (Deferred to UI Phase)"]
    S12["Stage 12: Backend & Integration Verification"]

    S1 --> S2
    S2 --> S4
    S3 --> S4
    S3 --> S5
    S4 --> S5
    S5 --> S6
    S5 --> S7
    S6 --> S7
    S7 --> S8
    S4 --> S9
    S6 -.-> S10
    S5 -.-> S10
    S6 -.-> S11
    S8 --> S12
    S9 --> S12
```

> [!TIP]
> **Backend & UI Decoupling**: Backend APIs (Stages 1–6), Sales Order dialog (Stages 7–8), and standard Frappe calendar/list views (Stage 9) form the core operational milestone. Stages 10 & 11 custom page UIs are stashed in `docs/development/ui/` and will be implemented during the dedicated front-end development phase.

