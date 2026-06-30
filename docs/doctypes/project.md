---
type: DocType Modification
title: Project Dashboard Modifications
description: Documentation for changes made to the Project DocType's connections dashboard.
resource: project
tags: [project, dashboard, doctype, customization]
---

# Project Dashboard Modifications

## Overview
The `induct_shop` application modifies the standard Frappe `Project` DocType's dashboard connections to align with the specific workflow requirements of the application.

## Form Modifications
The standard "Progress" tab is hidden on the Project DocType using a client-side script (`induct_shop/public/js/project.js`) via the `doctype_js` hook in `hooks.py`. To ensure the tab completely collapses in modern Frappe versions, this script explicitly iterates through and hides all constituent fields of the progress tab (e.g., `collect_progress`, `holiday_list`, etc.) across both `setup` and `refresh` form events.

## Dashboard Customizations
The following modifications have been made to the Project connections tab via the `override_dashboard` function in `induct_shop/induct_shop/overrides/project_dashboard.py`:

### Hidden Items
To streamline the interface, the following standard ERPNext document connections are hidden from the Project dashboard:
- Project Update
- Material Request
- BOM (Bill of Materials)
- Work Order

### Purchase Section Re-organization
The following documents have been moved to or grouped under the "Purchase" section:
- Stock Entry
- Expense Claim

### Sales Section Re-organization
The following documents have been grouped under the "Sales" section, ordered as follows:
- Quotation
- Sales Order
- Sales Invoice
- Delivery Note

## Technical Implementation
These changes are implemented by registering an `override_doctype_dashboards` hook in `hooks.py` for the `Project` DocType, which filters and regroups the `data["transactions"]` dictionary returned by the base Frappe dashboard generator.

## Costing Calculation Mechanism
The `induct_shop` app customizes the core ERPNext Project costing logic to include additional stock transactions. Two custom read-only fields have been added to the Project DocType to track these values:
- `custom_sales_stock_cost` (Sales Stock Cost): The aggregate stock value of Delivery Notes and Sales Invoices (with "Update Stock" checked) connected to the project.
- `custom_incoming_material_value` (Incoming Material Value): The aggregate incoming value from Stock Entries of type "Material Receipt" connected to the project.

### Technical Implementation
1. **Class Override**: The standard `Project` class is extended via `induct_shop.induct_shop.overrides.project.CustomProject` in `hooks.py`. The `update_costing()` method is overridden to query `Stock Ledger Entry` for the respective values and set the custom fields. The `calculate_gross_margin()` method is also overridden to factor these new values into the overall `expense_amount`.
2. **Document Events**: `doc_events` hooks are registered in `hooks.py` for `Delivery Note`, `Sales Invoice`, and `Stock Entry`. When these documents are submitted or cancelled, they trigger an asynchronous update (`erpnext.projects.doctype.project.project.update_costing_and_billing`) for all referenced projects.
