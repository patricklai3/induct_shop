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
The standard "Progress" tab is hidden on the Project DocType using a client-side script (`induct_shop/public/js/project.js`) via the `doctype_js` hook in `hooks.py`.

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
The following conclusions have been established for the future implementation of project cost calculations:
- **Sales Invoices with Stock Update**: If a Sales Invoice is submitted with the "Update Stock" option selected, the resulting stock transaction must count towards the cost of the given project.
- **Delivery Notes**: When a Delivery Note is made, its associated stock transaction should also count towards the cost of the project.
- **Incoming Material Value**: In the event of harvesting parts from a vehicle or acquiring core-return parts from a customer repair vehicle, a Stock Entry of type "Material Receipt" will be submitted. This results in incoming value (instead of outgoing value) that needs to be considered in the cost calculation as well.
