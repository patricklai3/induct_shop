---
type: Specification
title: "Technician Daily View UI (Stage 11)"
description: "Dedicated specification and implementation checklist for the Technician Daily View UI, deferred for future unified front-end development."
status: Deferred
tags: [scheduling, ui, technician, daily-view, front-end, specification, checklist]
timestamp: 2026-07-28T15:10:00Z
references:
  - docs/systems/scheduling-system.md
  - docs/archive/scheduling-implementation-checklist.md
---

# Technician Daily View UI (Stage 11)

> [!NOTE]
> This stage has been **deferred and stashed** for a future dedicated phase of unified front-end development. The underlying backend APIs (`get_technician_queue()`, employee user mapping, status transition methods) are implemented in Stage 6 (`induct_shop/api/technician_availability.py`).

---

## 1. Overview & Objectives

The **Technician Daily View** is a dedicated, mobile-friendly page providing each technician with a personal, read-optimized timeline of their workday. It answers the fundamental shop floor question for technicians: *"What job should I be working on right now?"*

### Key Goals
- Automatically resolve the logged-in user to their linked Employee record.
- Display a clear, chronological vertical timeline of assigned Schedule Entries.
- Explicitly surface idle gaps between jobs and shop break windows.
- Provide a prominent "Next Up" hero section with quick-action status transition ("Start Job").
- Allow shop managers to view any technician's daily queue via a dropdown selector.

---

## 2. UI Layout & Wireframe

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

---

## 3. Detailed Component Specifications

### 3.1 Automatic User Resolution & Technician Selector
- **Default Behavior**: On load, resolves `frappe.session.user` to an `Employee` record where `user_id = frappe.session.user`.
- **Manager Override**: Dropdown selector allowing staff with Manager roles to select any active technician to view their schedule.

### 3.2 Daily Summary Cards
Four summary badges rendered at the top:
1. **Total Jobs**: Number of Schedule Entries assigned for the date.
2. **Total Work Time**: Sum of pure work-minutes (formatted in hours & minutes, e.g., "6h 20m").
3. **Primary Bay**: Most frequently assigned bay for the technician on that date.
4. **Utilization %**: Percentage of operating hours filled by scheduled work (`utilization_pct`).

### 3.3 Vertical Timeline Rendering
- **Chronological Sequence**: Renders entries in order of `scheduled_time`.
- **Job Cards**: Show customer name, repair vehicle, service summary, assigned bay, duration, and status indicator.
- **Explicit Gap Display**: Idle periods between entries are displayed as distinct gap cards showing gap duration (e.g., "28min gap").
- **Lunch Break Block**: Rendered as a distinct hatched/shaded block in the timeline. Jobs spanning lunch display an inserted pause with work resuming post-lunch.

### 3.4 "Next Up" Hero Section & Action Panel
- Highlights the current or upcoming non-completed, non-cancelled Schedule Entry based on current system time.
- **Action Buttons**:
  - **"View Schedule Entry"**: Navigates directly to the Schedule Entry document form.
  - **"Start Job"**: One-click status transition changing entry status from `Scheduled` to `In Progress`.

---

## 4. API Dependencies

This page relies on existing backend endpoints in `induct_shop/api/technician_availability.py`:

- **`get_technician_queue(employee, date)`**: Returns ordered schedule entries, calculated lunch-aware effective end times, gap durations, and overall utilization metrics for a given technician and date.

---

## 5. Stashed Stage 11 Implementation Checklist

**Files to create in UI phase**: `induct_shop/induct_shop/page/technician_daily/` (JS, CSS, HTML/template, JSON specification)

- [ ] Create Frappe page asset structure (`technician_daily.js`, `technician_daily.json`, `technician_daily.css`).
- [ ] Build technician selector dropdown auto-defaulting to `frappe.db.get_value("Employee", {"user_id": frappe.session.user})`.
- [ ] Render summary cards (job count, total time, primary bay, utilization %).
- [ ] Implement vertical timeline layout for Schedule Entries matching data from `get_technician_queue()`.
- [ ] Render explicit gap cards between jobs with calculated gap durations.
- [ ] Render lunch break window as a distinct block in the timeline.
- [ ] Handle lunch-spanning jobs with split duration/pause visualization.
- [ ] Build "Next Up" hero footer bar highlighting the current/next entry.
- [ ] Implement "Start Job" button action (invokes status update `Scheduled` → `In Progress`).
- [ ] Wire "View Schedule Entry" button to navigate to form view.
- [ ] Add date navigation (prev/next day, today button).

---

## 6. Acceptance Criteria

- [ ] Auto-resolves logged-in employee ID correctly on page load.
- [ ] Dropdown permits managers to select and inspect any technician's schedule.
- [ ] Timeline rendering accurately matches output from `get_technician_queue()`.
- [ ] Gaps and lunch breaks are visually clear and chronologically accurate.
- [ ] Clicking "Start Job" successfully transitions Schedule Entry status to `In Progress`.
- [ ] "Next Up" card dynamically highlights the appropriate entry based on system time.
