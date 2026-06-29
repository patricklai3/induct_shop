---
type: DocType Modification
title: Quotation Customizations
description: Documentation for changes made to the Quotation DocType.
resource: quotation
tags: [quotation, doctype, customization, link, project]
---

# Quotation Customizations

## Overview
The `induct_shop` application modifies the standard Frappe `Quotation` DocType to ensure it links properly to other DocTypes used in the shop's workflows.

## Custom Fields
The following custom fields have been added to the Quotation DocType:

- **Project** (`project`): A Link field to the `Project` DocType, inserted after the `customer` field. This establishes a required connection so that Quotations correctly appear in the Project DocType's dashboard.

## Technical Implementation
These custom fields are packaged with the app and automatically installed via the `fixtures` export configuration (`"Custom Field"`) in `hooks.py`. The exported definition is stored in `induct_shop/fixtures/custom_field.json`.
