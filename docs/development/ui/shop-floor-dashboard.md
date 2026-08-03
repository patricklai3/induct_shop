---
type: Specification
title: "Shop Floor Dashboard UI (Stage 10)"
description: "Dedicated specification and implementation checklist for the Shop Floor Dashboard UI, deferred for future unified front-end development."
status: Deferred
tags: [scheduling, ui, dashboard, shop-floor, front-end, specification, checklist]
timestamp: 2026-07-28T15:10:00Z
references:
  - docs/systems/scheduling-system.md
  - docs/archive/scheduling-implementation-checklist.md
---

# Shop Floor Dashboard UI (Stage 10)

> [!NOTE]
> This stage has been **deferred and stashed** for a future dedicated phase of unified front-end development. The underlying backend APIs (`get_daily_technician_overview()`, bay availability checks, etc.) are implemented in Stage 6 (`induct_shop/api/technician_availability.py` and `induct_shop/api/scheduling.py`).

---

## 1. Overview & Objectives

The **Shop Floor Dashboard** is a per-bay day-strip timeline view designed specifically for shop floor managers. It provides an at-a-glance visualization of physical resource utilization (bays) alongside human resource capacity (technicians).

### Key Goals
- Display all active service bays as horizontal swim lanes across shop operating hours.
- Visualize job allocations, technician assignments, and job status in real time.
- Clearly highlight shop bottlenecks, unassigned appointments, and technician leave statuses.
- Support managerial actions such as bay reassignment and navigating to individual job or technician views.

---

## 2. UI Layout & Wireframe

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

---

## 3. Detailed Component Specifications

### 3.1 Bay Swim Lanes
- **Y-Axis**: Active Service Bays (filtered where `is_active = 1`). Inactive bays are hidden or grouped at the bottom.
- **X-Axis**: Shop operating hours (defined in `Shop Settings`, e.g., 08:00 to 17:00).
- **Job Blocks**: Renders Schedule Entry blocks positioned by `scheduled_time` and lunch-aware effective end time.
  - Displays customer name, vehicle description, assigned technician, and SO number.
  - **Color-Coded Statuses**:
    - `Scheduled`: Blue
    - `In Progress`: Amber
    - `Needs Review`: Red
    - `Completed`: Green
    - `Cancelled`: Hidden or greyed out

### 3.2 Capacity Summary Header
- **Active Bays Metric**: Count of active vs total Service Bays (e.g., "3 of 4 bays active").
- **Technician Workforce Metric**: Count of on-duty vs on-leave technicians (e.g., "2 of 3 techs on duty (1 on leave)").
- **Bottleneck Indicator**: Dynamically computed bottleneck from shop summary (e.g., "Bottleneck: Technicians").
- **Unassigned Alert**: Highlights count of entries lacking an assigned technician.

### 3.3 Lunch Break Visualization
- The lunch window (from `Shop Settings → break_start` to `break_end`) is rendered as a vertical hatched/shaded column across all bay lanes.
- Jobs that span lunch show a visual gap with the effective end time shifted accordingly.

### 3.4 Technician Load Panel (Collapsible Bottom Panel)
- Displays each active technician's daily workload.
- **Utilization Bar**: Visual fill bar representing `total_minutes / operating_minutes`.
- **Metrics**: Job count, utilization percentage (e.g., "79% · 4 jobs").
- **Leave Badge**: Technicians on approved leave feature a distinct `ON LEAVE` badge.
- **Unassigned Warning Section**: Lists all Schedule Entries for the date that do not have an `assigned_technician`.

---

## 4. API Dependencies

This page relies on existing backend endpoints in `induct_shop/api/technician_availability.py` and `induct_shop/api/scheduling.py`:

- **`get_daily_technician_overview(date)`**: Provides shop summary metrics, bay lane data, technician load percentages, and unassigned entries list.
- **`check_bay_availability(...)`**: Invoked on manual bay drag/reassignment to prevent double booking.

---

## 5. Stashed Stage 10 Implementation Checklist

**Files to create in UI phase**: `induct_shop/induct_shop/page/shop_floor/` (JS, CSS, HTML/template, JSON specification)

- [ ] Create Frappe page asset structure (`shop_floor.js`, `shop_floor.json`, `shop_floor.css`).
- [ ] Build bay swim lanes layout (Y-axis = bays, X-axis = operating hours).
- [ ] Render Schedule Entry blocks on correct bay lanes with customer, vehicle, technician, and status colors.
- [ ] Render lunch break column as a hatched/shaded vertical bar across all lanes.
- [ ] Render jobs spanning lunch with visual gap and shifted effective end time.
- [ ] Build Capacity Summary Header (active bays, on-duty/on-leave techs, bottleneck indicator, unassigned count).
- [ ] Add date navigation controls (prev/next day, today shortcut).
- [ ] Build Technician Load Panel (collapsible bottom section with utilization bars, job count, ON LEAVE labels).
- [ ] Highlight unassigned entries in the technician load panel.
- [ ] Wire block click events to navigate to `Form/Schedule Entry/<name>`.
- [ ] Wire technician bar click events to navigate to `page/technician_daily?employee=<id>`.

---

## 6. Acceptance Criteria

- [ ] Dashboard renders correctly with mock or live shop data (multiple bays, multiple entries, on-leave technicians).
- [ ] Bay swim lanes accurately reflect non-overlapping entries per bay.
- [ ] Lunch column visually spans all lanes cleanly.
- [ ] Technician load percentages match output from `get_daily_technician_overview()`.
- [ ] Unassigned entries are visually distinct and actionable.
- [ ] Navigation links to Schedule Entry forms and Technician Daily View function smoothly.
