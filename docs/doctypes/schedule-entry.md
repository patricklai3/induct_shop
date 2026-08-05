---
type: Reference
title: "Schedule Entry DocType"
description: "Documentation for the Schedule Entry DocType, managing appointment bookings for standalone diagnostics and repair jobs with capacity validation, provisional quick-entry, and P80 FRT duration estimation."
resource: schedule_entry
status: Implemented
tags: [doctype, scheduling, capacity, reference, quick-entry]
timestamp: 2026-08-05T14:10:00Z
---

# Schedule Entry DocType

The **Schedule Entry** DocType represents a scheduled service booking for diagnostic or repair work in the Induct Shop system. It supports both **standalone diagnostic intake** (using `Schedule Entry Type` records and provisional customer/vehicle text fields without requiring an existing Sales Order) and **repair bookings** (which enforce a 1:1 relationship with a submitted Sales Order). It dynamically validates bay and technician pool availability before saving.

---

## 1. Schema & Fields

| Fieldname | Fieldtype | Options | Description |
| :--- | :--- | :--- | :--- |
| `naming_series` | Select | `SE-.#####` | Automated naming series. |
| `entry_type` | Link | `Schedule Entry Type` | Type of booking (e.g., `Diagnostic`, `Repair`, `Meeting`; default: `Diagnostic`). |
| `sales_order` | Link | `Sales Order` | Linked submitted Sales Order (Required for Repair entries; optional for Diagnostic entries). |
| `customer` | Link | `Customer` | Master Customer reference (Optional/Editable; falls back to `provisional_customer_name`). |
| `provisional_customer_name` | Data | — | Quick-entry customer name when formal Customer record is not yet created. |
| `repair_vehicle` | Link | `Repair Vehicle` | Master Repair Vehicle (Optional/Editable; falls back to `provisional_vehicle_info`). |
| `provisional_vehicle_info` | Data | — | Quick-entry vehicle description when formal Repair Vehicle record is not yet created. |
| `scheduled_date` | Date | — | Date of the service appointment (Required). |
| `scheduled_time` | Time | — | Start time of the service appointment (Required). |
| `status` | Select | `Draft`, `Scheduled`, `Needs Review`, `In Progress`, `Completed`, `Cancelled` | Operational workflow status (Default: `Scheduled`). |
| `project` | Link | `Project` | Linked Project (Optional/Editable; populated on Check-in or SO link). |
| `vehicle_check_in` | Link | `Vehicle Check-in` | Linked intake document (Read Only; populated upon Vehicle Check-in). |
| `estimated_duration` | Int | — | Total duration in minutes (Auto-calculated via P80 FRT when SO present, or user-defined/60 mins for Diagnostic). |
| `service_bay` | Link | `Service Bay` | Assigned physical bay (Required). |
| `assigned_technician` | Link | `Employee` | Assigned technician (Filter: designation `Technician`). |
| `items_summary` | Long Text | — | Auto-generated summary of service items from the Sales Order (when SO present). |
| `notes` | Small Text | — | Optional internal staff scheduling notes. |

---

## 2. Controller Hooks & Logic

The `ScheduleEntry` Python controller (`induct_shop/induct_shop/doctype/schedule_entry/schedule_entry.py`) implements automated pre-save logic:

1. **`before_insert()`**:
   - Executes `populate_from_sales_order()` only if `sales_order` is populated. When `sales_order` is provided, fetches `customer`, `project`, and `repair_vehicle`, calculates risk-adjusted P80 `estimated_duration`, and generates `items_summary`.
   - Preserves user-defined or default duration (e.g. 60 mins for diagnostics) and provisional text fields when `sales_order` is omitted.

2. **Display Fallback Methods**:
   - `get_display_customer()`: Returns `customer_name` (or `customer` link) if set; otherwise falls back to `provisional_customer_name` or `"Unassigned Customer"`.
   - `get_display_vehicle()`: Returns `repair_vehicle` (or vehicle title/VIN) if set; otherwise falls back to `provisional_vehicle_info` or `"Unassigned Vehicle"`.

3. **`validate()`**:
   - **`validate_unique_sales_order()`**: Runs only when `sales_order` is set, enforcing that only one non-cancelled Schedule Entry can exist for any Sales Order (raises `frappe.DuplicateEntryError`).
   - **`validate_bay_availability()`**: Calls `check_bay_availability()` to verify the selected `service_bay` is free during the lunch-aware window (raises `frappe.ValidationError` on overlap for both standalone and SO-linked entries).
   - **`validate_technician_pool()`**: Calls `get_technician_pool_availability()` when `enable_technician_capacity` is active (raises `frappe.ValidationError` if shop-wide technician pool is exhausted).
   - **`validate_technician_assignment()`**: Performs soft overlap and approved leave checks for individual assigned technicians, raising visual warnings (`frappe.msgprint`) without blocking save.

---

## 3. Integration & UI Enhancements

- **Form Client Script (`schedule_entry.js`)**: Dynamically toggles field visibility (displaying master link fields when present, or provisional quick-entry fields when master records do not yet exist). Provides a custom **"Vehicle Check-in"** button on scheduled standalone appointments to open a pre-populated Vehicle Check-in quick form.
- **Calendar View (`schedule_entry_calendar.js`)**: Displays event titles using fallback display helpers (`get_display_customer()`, `get_display_vehicle()`) and renders event colors based on the linked `Schedule Entry Type.color`.
- **Sales Order Integration**: A "Schedule Service" button on submitted Sales Orders opens the interactive slot-picker modal (`induct_shop/public/js/sales_order.js`).
- **Amendment Handler**: When a Sales Order is amended (`sales_order_hooks.handle_amendment`), the linked `Schedule Entry` is re-linked to the new Sales Order version, its status changes to `Needs Review`, its `estimated_duration` is recalculated, and an Info Comment is attached if the updated duration creates a bay conflict.
