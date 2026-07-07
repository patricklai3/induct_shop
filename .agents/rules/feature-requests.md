---
trigger: model_decision
description: Apply this rule when creating or modifying features to ensure all feature requests are handled within the induct shop directory.
---

# Feature Requests Rule

All feature requests must be accomplished within the `induct shop` directory. When implementing new features, components, or enhancements, ensure that the code is placed and modified inside the `induct shop` application or directory structure, rather than in generic workspace folders or other apps, unless explicitly specified otherwise by the user.

Furthermore, all features MUST persist and be fully available upon a clean reinstall.
**CRITICAL: Never implement features using commands that insert doctype customizations directly into the database without exporting them to the codebase.** 
If a new DocType is required, you must define it programmatically as a **Standard DocType** (with JSON schema and Python controller files generated in the module's `doctype` directory) or explicitly export it as a fixture in `hooks.py`. Future agents must verify that their schema changes survive a `bench migrate` cycle.
**Handling Custom Fields (Preventing "Unknown Column" SQL Errors)**:
When a feature requires adding a custom field (e.g., `custom_frt`) to an existing standard DocType (like `Item`), you must ensure that:
1. The custom field is properly defined and tracked in the application (e.g., via `custom_fields` or `fixtures` in `hooks.py`, or created programmatically during setup).
2. When performing database queries (like `frappe.get_all` or `frappe.db.get_value`) that select these custom fields, you MUST defensively check if the column exists in the database first using `frappe.db.has_column(doctype, fieldname)`. This prevents hard application crashes (`MySQLdb.OperationalError: Unknown column`) in environments where the custom field has not yet been migrated or applied.