---
type: Reference
title: "Schedule Entry DocType"
description: "Documentation for the Schedule Entry DocType, managing appointment bookings linked to Sales Orders with automated P80 duration estimation and dual-resource capacity validation."
resource: schedule_entry
status: Implemented
tags: [doctype, scheduling, sales-order, capacity, reference]
timestamp: 2026-07-28T15:50:00Z
---

# Schedule Entry DocType

The **Schedule Entry** DocType represents a scheduled service booking for a vehicle repair job in the Induct Shop system. It enforces a strict **1:1 relationship** with a submitted ERPNext Sales Order, auto-populates project and vehicle context, and dynamically validates bay and technician pool availability before saving.

---

## 1. Schema & Fields

| Fieldname | Fieldtype | Options | Description |
| :--- | :--- | :--- | :--- |
| `naming_series` | Select | `SE-.#####` | Automated naming series. |
| `sales_order` | Link | `Sales Order` | Linked submitted Sales Order (**Unique**, required). |
| `customer` | Link | `Customer` | Auto-populated customer name (Read Only). |
| `scheduled_date` | Date | — | Date of the service appointment (Required). |
| `scheduled_time` | Time | — | Start time of the service appointment (Required). |
| `status` | Select | `Draft`, `Scheduled`, `Needs Review`, `In Progress`, `Completed`, `Cancelled` | Operational workflow status (Default: `Scheduled`). |
| `project` | Link | `Project` | Linked Project from Sales Order / Repair Vehicle (Read Only). |
| `repair_vehicle` | Link | `Repair Vehicle` | Linked Repair Vehicle derived from Project / SO (Read Only). |
| `estimated_duration` | Int | — | Total duration in minutes, auto-calculated via P80 FRT estimation. |
| `service_bay` | Link | `Service Bay` | Assigned physical bay (Required). |
| `assigned_technician` | Link | `Employee` | Assigned technician (Filter: designation `Technician`). |
| `items_summary` | Long Text | — | Auto-generated summary of service items from the Sales Order. |
| `notes` | Small Text | — | Optional internal staff scheduling notes. |

---

## 2. Controller Hooks & Logic

The `ScheduleEntry` Python controller (`induct_shop/induct_shop/doctype/schedule_entry/schedule_entry.py`) implements automated pre-save logic:

1. **`before_insert()`**:
   - `populate_from_sales_order()`: Automatically fetches `customer`, `project`, and `repair_vehicle`.
   - Calls `get_total_estimate()` over all service items on the Sales Order to calculate the risk-adjusted P80 `estimated_duration`.
   - Generates bulleted `items_summary`.

2. **`validate()`**:
   - **`validate_unique_sales_order()`**: Enforces that only one non-cancelled Schedule Entry can exist for any Sales Order (raises `frappe.DuplicateEntryError`).
   - **`validate_bay_availability()`**: Calls `check_bay_availability()` to verify the selected `service_bay` is free during the lunch-aware window (raises `frappe.ValidationError` on overlap).
   - **`validate_technician_pool()`**: Calls `get_technician_pool_availability()` when `enable_technician_capacity` is active (raises `frappe.ValidationError` if shop-wide technician pool is exhausted).
   - **`validate_technician_assignment()`**: Performs soft overlap and approved leave checks for individual assigned technicians, raising visual warnings (`frappe.msgprint`) without blocking save.

---

## 3. Integration & Amendment Flow

- **Sales Order Integration**: A "Schedule Service" button on submitted Sales Orders opens the interactive slot-picker modal (`induct_shop/public/js/sales_order.js`).
- **Amendment Handler**: When a Sales Order is amended (`sales_order_hooks.handle_amendment`), the linked `Schedule Entry` is re-linked to the new Sales Order version, its status changes to `Needs Review`, its `estimated_duration` is recalculated, and an Info Comment is attached if the updated duration creates a bay conflict.
