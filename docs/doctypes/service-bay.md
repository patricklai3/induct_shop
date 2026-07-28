---
type: Reference
title: "Service Bay DocType"
description: "Documentation for the Service Bay DocType and Service Bay Equipment child table, representing physical shop service bays and capability equipment tags."
resource: service_bay
status: Implemented
tags: [doctype, scheduling, service-bay, equipment, reference]
timestamp: 2026-07-28T15:50:00Z
---

# Service Bay DocType

The **Service Bay** DocType represents a physical work bay within the shop where repair operations take place. Each bay contains a set of capability equipment tags (via the `Service Bay Equipment` child table) used by the scheduling engine to filter capable bays for specific repair items.

---

## 1. Schema & Fields

### Service Bay (Parent DocType)

| Fieldname | Fieldtype | Options | Description |
| :--- | :--- | :--- | :--- |
| `bay_name` | Data | — | Unique name of the service bay (**Autoname & Title field**, Required). |
| `is_active` | Check | — | Active status flag (Default: `1`). Inactive bays are ignored during scheduling. |
| `description` | Small Text | — | Optional description of the bay setup or location. |
| `equipment` | Table | `Service Bay Equipment` | Child table storing equipment tags assigned to this bay. |

### Service Bay Equipment (Child Table)

| Fieldname | Fieldtype | Options | Description |
| :--- | :--- | :--- | :--- |
| `equipment_tag` | Link | `Equipment Tag` | Required equipment capability tag (e.g. `Lift`, `Alignment Rack`, `HV Battery Station`). |

---

## 2. API Integration & Capability Matching

- **`get_available_bays(date, start_time, duration_minutes, required_tags)`**:
  Fetches all active bays (`is_active=1`) whose equipment tags form a **superset** of the job's `required_tags`, and checks per-bay time window availability using `check_bay_availability()`.
- **`auto_assign_bay()`**:
  Automatically returns the first capable, unreserved bay matching the required equipment tags for a selected slot.
