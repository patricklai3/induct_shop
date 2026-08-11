---
type: Specification
title: "Quotation Approval System Extensions"
description: "Deferred extensions to the Quotation Approval System: Deferred Recommendation Tracking, Approval Analytics Dashboard, Multi-Quotation Approval Batching, and In-Person Tablet Approval Mode."
status: Deferred
tags: [specification, deferred, quotation, approval, analytics, recommendations, batching, tablet]
timestamp: 2026-08-10T16:41:00Z
---

# Quotation Approval System Extensions

These extensions were identified during the design of the [Quotation Approval System](file:///home/real2/projects/.project/frappe_docker/development/frappe-bench/apps/induct_shop/docs/development/quotation-approval-system-spec.md) and extracted here as deferred enhancements. Each builds upon the core approval infrastructure and can be implemented independently once the base system is operational.

---

## EXT-1: Deferred Recommendation Tracking

**Originating Section**: Quotation Approval System Spec, §4.5 (`on_submit` deferred item handling)

### Problem Statement

When customers defer quotation line items ("do this next visit"), those decisions are currently logged only as a `frappe.add_comment` on the parent `Project`. This unstructured text comment is difficult to query, surface contextually on subsequent visits, or report against for revenue recovery analysis.

### Proposed Solution

Create a lightweight **`Deferred Recommendation`** child table on the `Project` DocType (or a standalone link DocType) that captures structured deferred item data. When the customer returns for their next service, the advisor sees a contextual banner during `Vehicle Check-in` with outstanding deferred recommendations.

### Preliminary Schema: `Deferred Recommendation` (Child Table on `Project`)

| Field Name | Field Type | Options | Reqd | Description |
| :--- | :--- | :--- | :--- | :--- |
| `item_code` | Link | `Item` | Yes | The deferred item. |
| `item_name` | Data | — | No | Human-readable item description. |
| `original_quotation` | Link | `Quotation` | Yes | Quotation where the item was deferred. |
| `approval_record` | Link | `Quotation Approval Record` | No | The approval record that captured the deferral. |
| `deferred_date` | Date | — | Yes | Date the customer deferred the item. |
| `estimated_amount` | Currency | — | No | Quoted amount at time of deferral. |
| `customer_reason` | Small Text | — | No | Customer's stated reason for deferral. |
| `status` | Select | `Pending Follow-Up`, `Quoted on Next Visit`, `Completed`, `Cancelled` | Yes | Current follow-up status. |
| `follow_up_date` | Date | — | No | Suggested follow-up date. |

### Integration Points

- **Population**: `Quotation Approval Record.on_submit()` creates child rows for each item with `decision == 'Deferred'`.
- **Surfacing**: `Vehicle Check-in` controller queries `Deferred Recommendation` records for the same `Repair Vehicle` across all `Project` records and displays a banner if any have status `Pending Follow-Up`.
- **Revenue Reporting**: Enables structured queries like "total deferred revenue by month" or "most commonly deferred items."

### Dependencies

- Core approval system must be implemented first (specifically `Quotation Approval Record` and `Quotation Approval Item` DocTypes).
- Requires custom field additions to `Project` DocType.

---

## EXT-2: Approval Analytics Dashboard

**Originating Section**: Quotation Approval System Spec, §1 (operational visibility)

### Problem Statement

Shop management lacks visibility into approval conversion rates, average customer response times, and common rejection patterns. Without this data, managers cannot identify advisor training needs, pricing issues, or customer engagement bottlenecks.

### Proposed Solution

Create a **Quotation Approval Report** (Frappe Script Report in the `Induct Shop` module) with filters and aggregations against `Quotation Approval Record` data.

### Report Dimensions

| Metric | Calculation | Grouping Options |
| :--- | :--- | :--- |
| Approval Rate | `COUNT(Full Approval) / COUNT(all records)` | By period (week/month/quarter), by advisor |
| Partial Approval Rate | `COUNT(Partial Approval) / COUNT(all records)` | By period, by advisor |
| Rejection Rate | `COUNT(Full Rejection) / COUNT(all records)` | By period, by advisor |
| Average Response Time | `AVG(approval_datetime - quotation.creation)` for `Sent to Customer` → response | By channel (SMS/Email/Tablet) |
| Revenue Capture Rate | `SUM(approved_amount) / SUM(total_quoted_amount)` | By period, by advisor |
| Most Deferred Items | `COUNT(decision='Deferred') GROUP BY item_code` | Top 10 items |
| Channel Effectiveness | Approval rate grouped by `approval_channel` | By channel |

### Report Features

- Date range filter with preset options (This Week, This Month, This Quarter)
- Advisor filter (quotation owner)
- Customer filter
- Chart visualizations (bar chart for rates, line chart for trends)
- Drill-down from aggregate to individual `Quotation Approval Record` records

### Dependencies

- Requires sufficient `Quotation Approval Record` data volume for meaningful analysis.
- Core approval system must be implemented first.

---

## EXT-3: Multi-Quotation Approval Batching

**Originating Section**: Quotation Approval System Spec, §6 (customer-facing approval page)

### Problem Statement

Complex repair jobs (especially those involving mid-repair teardown discoveries) can produce multiple sequential quotations tied to the same `Project`. Under the base approval system, customers must approve each quotation independently, requiring separate links and separate approval sessions, which is cumbersome and increases the risk of missed approvals.

### Proposed Solution

Extend the customer-facing approval page (`/approve-quote`) to accept a `project` parameter in addition to the existing `token` parameter. When accessed via project, the page displays all pending quotations (those in `Sent to Customer` state) for that project in a single, unified approval session.

### Proposed UX Flow

1. Advisor clicks **"Send All Pending Quotes"** from the `Project` form.
2. System generates a project-level approval token (distinct from per-quotation tokens).
3. Customer opens a single link showing all pending quotations grouped by quotation number.
4. Customer makes per-line-item decisions across all quotations in one session.
5. On submit, the system creates individual `Quotation Approval Record` entries for each quotation (maintaining 1:1 record-to-quotation mapping) and processes each according to the standard Stage 3 flow.

### Technical Considerations

- **Token Scope**: Project-level tokens must validate against all pending quotations within the project, not just a single quotation. Token expiry applies globally.
- **Atomicity**: All quotation approval records should be created within a single database transaction to prevent partial submission states.
- **UI Complexity**: The approval page must clearly visually separate quotations while maintaining a unified decision submission button.
- **Fallback**: Individual per-quotation approval links remain fully functional for cases where only one quotation requires approval.

### Dependencies

- Core approval system (per-quotation approval) must be implemented and validated first.
- Project-level token generation requires additional custom fields on `Project`.

---

## EXT-4: Dedicated In-Person Tablet Approval Mode

**Originating Section**: Quotation Approval System Spec, §6.7 (In-Person Tablet Mode)

### Problem Statement

In the base MVP approval system, walk-in customers approve quotes using the exact same flow as remote customers: the advisor triggers a token link delivered via SMS/Email (or opened directly via link/QR code on a shop tablet or customer's phone). A dedicated "Tablet Mode" channel with kiosk locking, auto-refreshing sessions, and device hardware token pinning adds operational complexity that is unnecessary for initial launch.

### Proposed Solution

Create a specialized **In-Person Tablet Kiosk Handler** for physical shop tablets:
- Auto-generates in-shop tokens without requiring SMS/MMS gateway dispatch.
- Enforces kiosk security (prevents customer navigation away from the approval form).
- Automatically resets the tablet screen to a neutral "Hand back to advisor" state upon submission.
- Pins approval metadata with tablet hardware IDs for in-person audit logs.

### Interim Resolution

For MVP, walk-in customers receive and approve the estimate via the unified token link (SMS, email, or opening the standard token URL on an available tablet/phone). No dedicated tablet-only code or channel is required.

### Dependencies

- Core tokenized approval web page (`/approve-quote`) must be fully operational.
- Requires device/kiosk session management.
