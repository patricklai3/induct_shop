---
type: Reference
title: "Deferred Implementation Backlog"
description: "Master backlog index tracking deferred feature specifications, their originating specs, and current implementation status."
status: Active
tags: [reference, backlog, deferred, development, specifications]
timestamp: 2026-08-10T15:22:00Z
---

# Deferred Implementation Backlog

This directory contains specifications and technical feature modules that have been deferred from originating specifications into dedicated future implementation cycles.

## 1. Governance & Deferral Rules

1. **Extraction**: When a feature requirement is identified as out-of-scope or better suited for a dedicated subsystem, it is extracted into a standalone specification file within `docs/development/deferred/`.
2. **Originating Spec Linkage**: The originating specification MUST be updated to state the **Interim Resolution** (how the system functions currently) and include a direct link to the deferred specification.
3. **Master Registration**: Every deferred specification MUST be registered in the **Master Backlog Table** below.
4. **Promotion**: When work begins on a deferred item, its specification file is moved/promoted to `docs/development/<feature>-spec.md`, updated to status `Proposed` or `WIP`, and its status is updated in this index.

---

## 2. Master Backlog Table

| ID | Title / Feature | Originating Spec | Deferred Spec File | Status | Date Deferred |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEF-001` | User Roles & Permissions Governance | [quotation-approval-system-spec.md](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/quotation-approval-system-spec.md) | [user-roles-and-permissions-spec.md](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/deferred/user-roles-and-permissions-spec.md) | Deferred | 2026-08-10 |
