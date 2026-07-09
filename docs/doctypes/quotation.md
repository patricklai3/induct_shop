---
type: Reference
title: Quotation Customizations
description: Documentation for changes made to the Quotation DocType.
resource: quotation
tags: [doctype, quotation, customization]
status: Implemented
---

# Quotation Customizations

## Overview
The `induct_shop` application modifies the standard Frappe `Quotation` DocType to ensure it links properly to other DocTypes used in the shop's workflows.

## Custom Fields
The following custom fields have been added to the Quotation DocType:

- **Project** (`project`): A Link field to the `Project` DocType, inserted after the `customer` field. This establishes a required connection so that Quotations correctly appear in the Project DocType's dashboard.

## Client Scripts
The following client-side scripts are injected into the Quotation DocType:

- **Customer Fetching**: A script (`induct_shop/public/js/quotation.js`) is injected via the `doctype_js` hook. When a Quotation is created from the Project dashboard, the `project` field is automatically populated. This script listens for changes to the `project` field (and initial `setup` loads). If a project is selected but no customer is set, it queries the backend for the project's linked customer and dynamically sets the `quotation_to` (to "Customer") and `party_name` fields on the Quotation. This automatically triggers standard ERPNext frontend logic to pull in the customer's address, contact info, and active price list.

## Technical Implementation
The custom fields are packaged with the app and automatically installed via the `fixtures` export configuration (`"Custom Field"`) in `hooks.py`. The exported definition is stored in `induct_shop/fixtures/custom_field.json`.

The client scripts are implemented in `induct_shop/public/js/quotation.js` and loaded dynamically into the Quotation view by defining `"Quotation"` within the `doctype_js` dictionary in `hooks.py`.
