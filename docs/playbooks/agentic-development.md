---
type: Playbook
title: Agentic Development in Frappe
description: Workflow for provisioning features and doctypes programmatically without the Frappe UI.
tags: [development, agent, workflow, frappe]
timestamp: 2026-06-27T07:16:00Z
---

# Overview

When developing without the Frappe UI using agentic coding tools, developers should lean on programmatic scaffolding via short Python scripts to ensure the database and filesystem are perfectly synchronized.

# Scaffolding DocTypes

Instead of manually creating `.json` and `.py` files, use a Python script executed via the `bench` CLI to leverage Frappe's internal hooks for generating boilerplate files.

## Example Script

```python
import frappe

def execute():
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Tesla Vehicle",
        "module": "Induct Shop",
        "custom": 0, # CRITICAL: 0 means it writes to disk
        "fields": [
            {"fieldname": "vin", "fieldtype": "Data", "label": "VIN", "reqd": 1},
            {"fieldname": "model", "fieldtype": "Select", "label": "Model", "options": "Model S\nModel 3\nModel X\nModel Y"}
        ]
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
```

Run this script using the `bench execute` command:

```bash
bench --site development.localhost execute induct_shop.scaffold_vehicle.execute
```

This ensures the `apps/induct_shop/induct_shop/induct_shop/doctype/` directory is properly scaffolded.

# Modifying Vanilla Workflows

To modify standard DocTypes (e.g., Sales Invoice or Project) while ensuring changes survive a reinstall:

1. Ensure your `hooks.py` has `fixtures = ["Custom Field", "Property Setter"]`.
2. Write a script to programmatically create `Custom Field` records.
3. Run `bench --site development.localhost export-fixtures`.
4. Run `bench --site development.localhost clear-cache`.
