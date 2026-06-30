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
The custom costing mechanism for projects is implemented via a Python override (`induct_shop.overrides.project.CustomProject`) registered via `override_doctype_class`.

The standard gross margin and costing logic is extended with two custom fields:
- **Sales Stock Cost** (`custom_sales_stock_cost`): Sums the stock value difference of all outgoing stock from Delivery Notes and Sales Invoices (when "Update Stock" is selected) connected to the project. This amount is added to the total `expense_amount`.
- **Incoming Material Value** (`custom_incoming_material_value`): Sums the incoming value of parts harvested or acquired via Stock Entries of type "Material Receipt" connected to the project. This incoming value reduces the total `expense_amount`.

Additionally, the `hooks.py` registers `on_submit` and `on_cancel` events for `Delivery Note`, `Sales Invoice`, and `Stock Entry` documents to automatically recalculate and synchronize the linked project's costing when any of these documents change.
