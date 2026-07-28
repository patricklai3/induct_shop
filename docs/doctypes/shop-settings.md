---
type: Reference
title: "Shop Settings DocType"
description: "Documentation for the Shop Settings singleton DocType, managing global shop operating hours, lunch break windows, slot intervals, technician designation filters, and capacity toggles."
resource: shop_settings
status: Implemented
tags: [doctype, scheduling, shop-settings, configuration, reference]
timestamp: 2026-07-28T15:50:00Z
---

# Shop Settings DocType

The **Shop Settings** DocType is a **Singleton** configuration document that defines the operational boundaries and feature toggles for the Induct Shop scheduling system.

---

## 1. Schema & Fields

| Fieldname | Fieldtype | Default | Description |
| :--- | :--- | :--- | :--- |
| `operating_hours_start` | Time | `08:00:00` | Shop opening time. |
| `operating_hours_end` | Time | `17:00:00` | Shop closing time. |
| `break_start` | Time | `12:00:00` | Start of shop-wide lunch break. |
| `break_end` | Time | `12:30:00` | End of shop-wide lunch break. |
| `default_slot_interval` | Int | `30` | Slot picker grid interval in minutes. |
| `holiday_list` | Link (`Holiday List`) | — | Linked ERPNext Holiday List for holiday slot exclusion. |
| `scheduling_horizon_days` | Int | `30` | Maximum booking horizon in days. |
| `technician_designation` | Link (`Designation`) | `Technician` | Employee designation filter used to identify shop technicians. |
| `enable_technician_capacity` | Check | `1` | Feature toggle for technician pool capacity gating. |

---

## 2. Behavioral Impact

- **Lunch-Aware Calculation**: `effective_end_time()` reads `break_start` and `break_end` to extend job clock-end times when a appointment spans the lunch break window.
- **Technician Capacity Toggle**: When `enable_technician_capacity = 0`, scheduling capacity checks skip technician pool evaluation and operate in pure bay-capacity mode.
