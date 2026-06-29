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
