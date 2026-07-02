---
type: Playbook
title: "How to Clean Up Customizations on Uninstall"
description: "Instructions and overview of the app uninstallation hook used to remove custom fields and other customizations."
tags: [playbook, maintenance, uninstall]
timestamp: 2026-06-29T16:40:00Z
---

When the `induct_shop` application is uninstalled from a site, it is important to remove any custom fields, property setters, or scripts that were injected into standard ERPNext/Frappe DocTypes during its lifecycle. This prevents orphaned customizations and ensures a clean state for testing or subsequent reinstallations.

# Uninstall Hook Integration

The cleanup logic is triggered via the `before_uninstall` hook. In `hooks.py`, the following registration is made:

```python
before_uninstall = "induct_shop.uninstall.before_uninstall"
```

# Cleanup Script Details

The cleanup logic resides in `induct_shop/uninstall.py`. When `bench uninstall-app induct_shop` is executed, the script automatically performs the following:

1. **Dynamic Removal by Module:** It searches for all `Custom Field`, `Property Setter`, `Client Script`, and `Server Script` records where the `module` is explicitly set to `"Induct Shop"`. These are then deleted using `frappe.delete_doc()`.
2. **Explicit Fallback Removal:** To handle any legacy fields or custom fields added without the correct module tag, the script maintains an explicit list of field names (e.g., `Quotation-repair_vehicle`) and attempts to delete them if they exist in the database.

# Best Practices

When adding new customizations programmatically or via the Frappe UI:
- Always ensure the **Module** field is set to `Induct Shop`. This guarantees the dynamic cleanup routine will catch them.
- If a custom field is created without the module tag and cannot be easily updated, add its specific name (e.g., `DocType-fieldname`) to the `explicit_fields` list inside `induct_shop/uninstall.py` to ensure it gets removed on app uninstallation.
