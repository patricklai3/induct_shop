---
type: Specification
title: "User Roles & Permissions Management Specification"
description: "Dedicated specification for custom shop user roles (Shop Manager, Service Advisor, Shop Technician) and granular permission matrices across Induct Shop modules."
status: Deferred
originating_specs:
  - "docs/development/quotation-approval-system-spec.md"
tags: [specification, roles, permissions, governance, security, deferred]
timestamp: 2026-08-10T15:22:00Z
---

# User Roles & Permissions Management Specification

## 1. Context & Deferral Rationale

This specification captures requirements for custom shop user role definitions and permission controls across the `induct_shop` application.

This feature requirement originally emerged during the design of the [Dual-Stage Quotation Approval System](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/quotation-approval-system-spec.md) (Section 8 "New Roles"), where custom roles (`Shop Manager`, `Service Advisor`) were proposed to provide shop-specific access control beyond default ERPNext roles.

To maintain focus and avoid scope creep during the initial Quotation Approval System implementation, custom role creation has been **deferred** to this dedicated specification.

> [!IMPORTANT]
> **Interim Phase 1 Resolution**:
> The Quotation Approval System will utilize native Frappe/ERPNext roles (`Sales User` for Service Advisors, `Sales Manager` for Shop Managers) for state transitions and workflow permissions.

---

## 2. Technical Scope & Requirements

### 2.1 Proposed Custom Roles

| Role Name | Description & Purpose | Originating Context | Initial Required Permissions |
| :--- | :--- | :--- | :--- |
| `Shop Manager` | Dedicated role for shop operational management. Can approve internal high-value quotations, override discounts, and access shop management reports. | [quotation-approval-system-spec.md](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/quotation-approval-system-spec.md) | Read, Write, Submit, Cancel, Amend on `Quotation`, `Quotation Approval Record`, `Shop Settings`. |
| `Service Advisor` | Dedicated role for customer-facing service personnel. Can compose quotations, trigger customer approval links, and manage service check-ins. | [quotation-approval-system-spec.md](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/quotation-approval-system-spec.md) | Read, Write, Submit on `Quotation`, `Vehicle Check-in`. Read on `Quotation Approval Record`. |
| `Shop Technician` | Dedicated role for workshop mechanics. Can view approved job lines, update labor progress, and record vehicle inspection notes. | Workshop Management | Read on `Quotation Approval Record`, Write on `Vehicle Check-in` inspection notes. |

### 2.2 Granular Access Control Matrix

*(To be fully defined upon active development)*

- Role Permission Manager fixtures (`Role`, `Custom DocPerm`) exported in `induct_shop`.
- User Permission restrictions (e.g., scoping advisors and managers to specific shop branches or locations).
- Custom field access control (e.g., hiding financial margin calculations from standard `Service Advisor` role).

---

## 3. Promotion Checklist

When this specification is selected for active implementation:
- [ ] Move file from `docs/development/deferred/user-roles-and-permissions-spec.md` to `docs/development/user-roles-and-permissions-spec.md`.
- [ ] Update frontmatter `status` from `Deferred` to `Proposed`.
- [ ] Update `docs/development/deferred/index.md` status to `In Development`.
- [ ] Generate standard implementation checklist using `/generate-checklist`.
