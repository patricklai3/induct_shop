---
type: Reference
title: "Induct Shop OKF Standards"
description: "Domain-specific extension of OKF for the induct_shop repository."
tags: [reference, specification, okf, standards]
timestamp: 2026-07-02T00:00:00Z
---

# Induct Shop OKF Standards

**Version 1.0**

This document serves as the strict, domain-specific extension of the base [Open Knowledge Format (OKF)](/okf-spec.md) for the `induct_shop` repository. While the base OKF specification is permissive, these internal standards must be followed for all documentation (`.md`) files within the `docs/` directory to ensure consistency, accurate agent traversal, and predictable organization.

---

## 1. Universal Frontmatter Schema

Every concept document in the repository MUST use the following YAML frontmatter schema:

```yaml
---
type: [Strict Type]           # REQUIRED (Must be from the Approved Types list below)
title: "[Human Title]"        # RECOMMENDED (The human-readable name of the concept)
description: "[Summary]"      # RECOMMENDED (A single sentence summarizing the document)
resource: [URI or ID]         # OPTIONAL (Use snake_case ID for Frappe assets, or external URL)
status: [Status]              # OPTIONAL (E.g., Proposed, Implemented, Deprecated)
tags: [tag1, tag2, ...]       # RECOMMENDED (Categorization tags, see Section 3)
timestamp: YYYY-MM-DDTHH:MM:SSZ # RECOMMENDED (ISO-8601 timestamp of last major update)
---
```

---

## 2. Approved `type` Taxonomy

To prevent fragmentation (e.g., mixing `DocType Specification`, `Reference`, `DocType`), all documents MUST use one of the following exact `type` strings. No other types are permitted.

| `type` | Description | Typical Directory |
| :--- | :--- | :--- |
| **`Reference`** | Documentation for a finalized, implemented technical asset (e.g., a DocType, a Module, an API endpoint). | `docs/doctypes/`, `docs/api/` |
| **`Specification`** | A proposed feature, schema, or technical design that is not yet fully implemented. | `docs/proposals/`, `docs/doctypes/` |
| **`Playbook`** | Step-by-step instructions or operational procedures for humans (e.g., "How to uninstall customizations"). | `docs/playbooks/`, `docs/sops/` |
| **`Script`** | Documentation detailing backend/frontend automation (Python hooks, JS Client Scripts). | `docs/scripts/`, `docs/automations/` |
| **`System`** | High-level architectural documentation describing infrastructure, servers, or environment setups. | `docs/systems/` |
| **`Business Process`** | Non-technical documentation describing how the shop operates. | `docs/business/` |

---

## 3. Tagging Conventions

The `tags` array SHOULD be used aggressively for cross-cutting concerns to allow both humans and agents to filter related knowledge.

1. **Asset Category Tag**: The first tag should broadly identify the asset type (e.g., `doctype`, `script`, `playbook`, `infrastructure`).
2. **Domain Tags**: Include relevant shop domains (e.g., `vehicle`, `check-in`, `billing`, `inventory`, `project`).
3. **State Tags**: Use tags like `draft`, `wip`, or `archived` if applicable.

---

## 4. Examples

### Example 1: An Implemented Frappe DocType
```yaml
---
type: Reference
title: "Repair Vehicle DocType"
description: "Documentation for the Repair Vehicle DocType and its integrated Tesla VIN Decoder."
resource: repair_vehicle
status: Implemented
tags: [doctype, vehicle, tesla]
timestamp: 2026-06-27T08:37:00Z
---
```

### Example 2: A Proposed Feature
```yaml
---
type: Specification
title: "Vehicle Health Check"
description: "Specification and feature list for the proposed Vehicle Health Check DocType."
resource: vehicle_health_check
status: Proposed
tags: [doctype, specification, vehicle, inspection]
timestamp: 2026-07-02T00:15:00Z
---
```

### Example 3: A Maintenance Playbook
```yaml
---
type: Playbook
title: "How to Clean Up Customizations on Uninstall"
description: "Steps and scripts to remove Frappe customizations injected by the app upon uninstallation."
tags: [playbook, maintenance, uninstall, frappe]
timestamp: 2026-06-29T23:00:19Z
---
```
