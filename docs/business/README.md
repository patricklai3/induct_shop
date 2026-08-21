---
type: Playbook
title: "Business Vault Governance & Lifecycle Protocol"
description: "Operational guide and lifecycle management protocol governing the business documentation vault."
status: Active
tags: [governance, business, okf, operations, lifecycle, protocol]
timestamp: 2026-08-20T17:10:00Z
---

# Business Vault Governance & Lifecycle Protocol

This document establishes the operational rules and lifecycle mechanics governing the `docs/business/` directory. It ensures that both human contributors and AI agents interact with the business knowledge base with absolute consistency, preserving decision history while maintaining an authoritative single source of truth for active business operations.

---

## 1. Directory Purpose & Core Philosophy

The `docs/business/` knowledge vault is dedicated to capturing and managing all non-code, commercial, operational, and facility aspects of Induct Shop — starting with the shop opening initiative and extending into ongoing operations. Active milestones and task deliverables are tracked live on the [Shop Opening GitHub Project (Project 13)](https://github.com/users/patricklai3/projects/13).

It mirrors the promotion lifecycle established in the software development directory (`docs/development/` $\rightarrow$ `docs/systems/` / `docs/doctypes/`):

```
+------------------------------------+
|  docs/business/in-progress/        |  Active Decision Checklists, RFPs,
|  (Parameter Checklists & Blanks)   |  Quote Comparisons, Target Values
+-----------------+------------------+
                  |
         [ Decision Reached & Signed Off ]
                  |
                  v
+-----------------+------------------+      +------------------------------------+
|  docs/business/established/        |      |  docs/business/archive/            |
|  (Official Source of Truth)        | <--- |  (Historical Evaluation Record &   |
|  Policy Numbers, SOPs, Terms       |      |   Original Decision Rationale)     |
+------------------------------------+      +------------------------------------+
```

---

## 2. Three-Stage Lifecycle Progression

### Stage 1: In-Progress (`docs/business/in-progress/`)
- **Document Type**: `type: Specification` or `type: Business Process` (`status: In Progress` or `status: Proposed`).
- **Content Structure**: Formatted with owner-fillable blanks (`______`) and actionable task/decision checkboxes (`[ ]`). Contains parameter checklists, candidate quote comparison tables, open questions, and sign-off sections.
- **Rule for AI Agents**:
  - Prompt owners for missing parameter values rather than assuming numbers.
  - Fill in candidate vendor quotes and comparison metrics upon request.
  - Never mark decision checkboxes as completed (`[x]`) unless explicitly confirmed by the business owners.

### Stage 2: Established Realities (`docs/business/established/`)
- **Document Type**: `type: Business Process` or `type: Reference` (`status: Active`).
- **Content Structure**: The authoritative, factual description of finalized business realities (e.g., active insurance policy numbers and claim procedures, executed lease covenants and facility dimensions, commissioned equipment inventory and warranty contacts, production IT network topology).
- **Rule for AI Agents**:
  - Treat all documents in `established/` as immutable operational facts.
  - Cross-reference established documents when generating standard operating procedures, workflows, or developer specifications.
  - Only update established documents when an official change occurs (e.g., policy renewal, equipment replacement, lease amendment).

### Stage 3: Archived Decisions (`docs/business/archive/`)
- **Document Type**: `type: Specification` or `type: Reference` (`status: Archived`).
- **Content Structure**: The original in-progress evaluation document, moved into `docs/business/archive/` upon decision finalization.
- **Rule for AI Agents**:
  - When a decision is finalized, move the original spec to `archive/` (or create an archive entry) with `status: Archived`.
  - Add a banner at the top linking directly to the new active document in `docs/business/established/`.
  - Retain the historical context, candidate quotes that were rejected, and rationale for auditability.

---

## 3. Standard Document Formats & OKF Compliance

All documents within `docs/business/` must adhere strictly to the [Open Knowledge Format (OKF)](/standards/okf-spec.md) and the [Induct Shop OKF Standards](/standards/induct-okf-standard.md).

### 3.1 YAML Frontmatter Requirements
Every non-index markdown file MUST start with a valid YAML frontmatter block:

```yaml
---
type: Business Process            # Must be an approved type (Business Process, Specification, Reference, Playbook)
title: "Document Title"           # Human-readable title
description: "Single sentence summary."
status: In Progress               # In Progress | Proposed | Active | Implemented | Archived
tags: [business, category, ...]   # Categorization tags
timestamp: YYYY-MM-DDTHH:MM:SSZ   # ISO-8601 timestamp of last major update
---
```

### 3.2 Reserved Filenames
- `index.md`: Reserved strictly for directory navigation listings. **Must NOT contain frontmatter** (per OKF §6).
- All concept files must use descriptive kebab-case names (e.g., `site-selection-spec.md`, `commercial-insurance.md`).

---

## 4. Operational Step-by-Step Instructions

### How to Add a New Business Initiative
1. Create a new markdown file in `docs/business/in-progress/<initiative-name>-spec.md`.
2. Apply the `type: Specification` frontmatter with `status: In Progress`.
3. Structure the document with parameter checklists with fill-in blanks (`[ ] Parameter: ______`), candidate comparison matrices, and owner sign-off checkboxes.
4. Register the new document in [`docs/business/in-progress/index.md`](./in-progress/index.md) and [`docs/business/index.md`](./index.md).

### How to Promote an Initiative to Established
1. Verify that all required decision checkboxes in the in-progress specification are marked complete (`[x]`) and signed off by the owners.
2. Author the new authoritative operational document in `docs/business/established/<topic>.md` with `type: Business Process` or `type: Reference` and `status: Active`. Include actionable details: contacts, policy numbers, claim workflows, serial numbers, and covenants.
3. Move or copy the completed evaluation document to `docs/business/archive/<initiative-name>-spec.md` with `status: Archived` and link it to the established document.
4. Update [`docs/business/in-progress/index.md`](./in-progress/index.md), [`docs/business/established/index.md`](./established/index.md), [`docs/business/archive/index.md`](./archive/index.md), and the master [`docs/business/index.md`](./index.md).
5. Add a dated log entry in [`docs/log.md`](/log.md).
