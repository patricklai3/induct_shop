---
type: Specification
title: "Standalone Diagnostic Scheduling Implementation Checklist"
description: "Staged development checklist tracking implementation, schema updates, UI enhancements, automated tests, manual verification, and documentation."
status: In Progress
tags: [checklist, scheduling, development, tracking]
timestamp: 2026-08-04T15:53:00Z
---

# Standalone Diagnostic Scheduling Implementation Checklist

This checklist tracks the staged implementation of standalone capacity-blocking scheduling, the `Schedule Entry Type` DocType, disposable quick-entry context fields, and vehicle intake integration in `induct_shop`.

---

## Stage 1: `Schedule Entry Type` DocType & Seed Data
- [ ] **1.1 Schema Definition**: Create standard `Schedule Entry Type` DocType in `induct_shop/induct_shop/doctype/schedule_entry_type/`:
  - `schedule_entry_type.json`: Define `type_name` (Data, reqd, unique, title_field), `color` (Data), `description` (Small Text), `requires_sales_order` (Check).
  - `schedule_entry_type.py`: Implement Python controller.
- [ ] **1.2 Standard Seed Data**: Add seed data setup (or `after_install`/migration hook) for standard entry types:
  - `Diagnostic` (Requires SO: `0`, Color: `#1f538d`)
  - `Repair` (Requires SO: `1`, Color: `#2e7d32`)
  - `Meeting` (Requires SO: `0`, Color: `#7b1fa2`)
  - `Maintenance / Shop Cleaning` (Requires SO: `0`, Color: `#c62828`)
  - `Internal Service` (Requires SO: `0`, Color: `#ef6c00`)

### Stage 1 Acceptance Criteria
- **Automated Testing Criteria**:
  - `frappe.get_doc("Schedule Entry Type", "Diagnostic")` exists and has `requires_sales_order = 0`.
  - All 5 standard seed records (`Diagnostic`, `Repair`, `Meeting`, `Maintenance / Shop Cleaning`, `Internal Service`) exist in DB.
- **Manual Review Criteria**:
  - Open Desk -> **Schedule Entry Type List** -> verify all 5 default types are listed with colors and descriptions.

---

## Stage 2: `Schedule Entry` Schema & Controller Refactoring
- [ ] **2.1 Schema Updates (`schedule_entry.json`)**:
  - Add Link field `entry_type` -> `Schedule Entry Type` (default: `Diagnostic`).
  - Modify `sales_order`: set `reqd: 0`, remove schema-level `unique: 1`.
  - Modify `customer`: set `reqd: 0` (optional), remove `read_only`.
  - Modify `repair_vehicle`: set `reqd: 0` (optional), remove `read_only`.
  - Modify `project`: set `reqd: 0` (optional), remove `read_only`.
  - Add `provisional_customer_name` (Data, "Customer Name (Quick Entry)").
  - Add `provisional_vehicle_info` (Data, "Vehicle Description (Quick Entry)").
  - Add Link field `vehicle_check_in` -> `Vehicle Check-in` (read-only).
- [ ] **2.2 Controller Refactoring (`schedule_entry.py`)**:
  - Update `before_insert()`: Auto-populate from `sales_order` only if `sales_order` is set; otherwise preserve user-defined duration and fields.
  - Implement `get_display_customer()` and `get_display_vehicle()` fallback helper methods.
  - Update `validate_unique_sales_order()` to execute only when `sales_order` is populated.
  - Verify capacity validation (`validate_bay_availability`, `validate_technician_pool`, `validate_technician_assignment`) works correctly for standalone entries.

### Stage 2 Acceptance Criteria
- **Automated Testing Criteria**:
  - Can create and save `Schedule Entry` with `entry_type = "Diagnostic"`, `scheduled_date`, `scheduled_time`, `service_bay`, `estimated_duration = 60`, `provisional_customer_name = "John Phone"`, omitting `sales_order`, `customer`, and `repair_vehicle`.
  - Overlapping standalone entry on the same bay during the same time window raises `frappe.ValidationError` (capacity gating verified).
  - `doc.get_display_customer()` returns `"John Phone"` when `customer` link is empty, and returns `customer_name` when `customer` link is populated.
- **Manual Review Criteria**:
  - Desk Form -> New Schedule Entry -> Fill Date, Time, Bay, and "Customer Name (Quick Entry)" without picking a Sales Order or Customer -> Save document successfully.

---

## Stage 3: `Vehicle Check-in` Integration & Cross-Linking
- [ ] **3.1 Schema Update (`vehicle_check_in.json`)**:
  - Add Link field `schedule_entry` -> `Schedule Entry`.
- [ ] **3.2 Controller Hook (`vehicle_check_in.py`)**:
  - In `after_insert()`, when `Project` is auto-created, write `project`, `repair_vehicle`, `customer`, and `vehicle_check_in` links back to the originating `Schedule Entry`.

### Stage 3 Acceptance Criteria
- **Automated Testing Criteria**:
  - Creating `Vehicle Check-in` linked to a standalone `Schedule Entry` auto-creates a `Project` and updates the `Schedule Entry` with `project`, `repair_vehicle`, `customer`, and `vehicle_check_in` references.
- **Manual Review Criteria**:
  - Perform Vehicle Check-in for an appointment -> Verify the originating `Schedule Entry` displays the created `Project` and `Repair Vehicle` links.

---

## Stage 4: Form UI & Calendar Enhancements
- [ ] **4.1 Form Client Script (`schedule_entry.js`)**:
  - Dynamic field visibility: show `sales_order` / master link fields when present, show provisional quick-entry fields when master records do not exist.
  - Add **"Vehicle Check-in"** custom action button when `status == "Scheduled"` and no `vehicle_check_in` is linked.
- [ ] **4.2 Calendar Client Script (`schedule_entry_calendar.js`)**:
  - Update title formatting to use fallback display helpers (`get_display_customer()` / `get_display_vehicle()`).
  - Render event colors using linked `Schedule Entry Type.color`.

### Stage 4 Acceptance Criteria
- **Automated Testing Criteria**:
  - `bench build` or JS compilation passes cleanly with zero syntax errors.
- **Manual Review Criteria**:
  - Open `Schedule Entry` Form -> confirm quick entry fields render when `sales_order` is empty and **"Vehicle Check-in"** button appears for scheduled entries.
  - Open **Schedule Entry Calendar View** -> verify standalone entries display provisional customer/vehicle names with entry type colors.

---

## Stage 5: Automated Testing Suite & Clean Migration
- [ ] **5.1 Unit Tests (`test_schedule_entry.py`)**:
  - Test creation of `Schedule Entry Type` records.
  - Test standalone `Schedule Entry` creation with zero master records (only provisional text fields). Assert save succeeds and bay/technician capacity validation blocks overlapping slots.
  - Test `Vehicle Check-in` linkage and automatic project cross-referencing to `Schedule Entry`.
  - Test `Sales Order` creation and linking for repair entries.
- [ ] **5.2 Migration & Reinstall Verification**:
  - Execute `bench --site development.localhost run-tests --app induct_shop` inside Docker container to ensure all tests pass cleanly.

### Stage 5 Acceptance Criteria
- **Automated Testing Criteria**:
  - Docker command `bench --site development.localhost run-tests --app induct_shop` completes with 100% pass rate.
  - `bench migrate` completes cleanly without database error tracebacks.
- **Manual Review Criteria**:
  - Execute full dry run: Schedule Diagnostic -> Vehicle Check-in -> Quotation -> Sales Order -> Repair Schedule.

---

## Stage 6: Documentation & Workflow Alignment
- [ ] **6.1 Update Primary Workflow Doc (`docs/workflow.md`)**:
  - Update business process text and Mermaid flow diagram to document flexible diagnostic intake.
- [ ] **6.2 Update DocType Documentation**:
  - Update `docs/doctypes/schedule-entry.md`.
  - Update `docs/doctypes/vehicle-check-in.md`.

### Stage 6 Acceptance Criteria
- **Automated Testing Criteria**:
  - All modified docs pass OKF validation (valid YAML frontmatter `type: Specification` / `Business Process` / `Reference`, valid tags, no broken links).
- **Manual Review Criteria**:
  - Review updated Mermaid workflow diagram in `docs/workflow.md`.
