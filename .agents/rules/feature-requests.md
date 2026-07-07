---
trigger: model_decision
description: Apply this rule when creating or modifying features to ensure all feature requests are handled within the induct shop directory.
---

# Feature Requests Rule

All feature requests must be accomplished within the `induct shop` directory. When implementing new features, components, or enhancements, ensure that the code is placed and modified inside the `induct shop` application or directory structure, rather than in generic workspace folders or other apps, unless explicitly specified otherwise by the user.

Furthermore, all features must be available upon reinstall. This means they cannot be achieved through commands that insert doctype customizations directly into the database; instead, they must be committed to the application codebase as standard fixtures or schema definitions.

**Handling Custom Fields (Preventing "Unknown Column" SQL Errors)**:
When a feature requires adding a custom field (e.g., `custom_frt`) to an existing standard DocType (like `Item`), you must ensure that:
1. The custom field is properly defined and tracked in the application (e.g., via `custom_fields` or `fixtures` in `hooks.py`, or created programmatically during setup).
2. When performing database queries (like `frappe.get_all` or `frappe.db.get_value`) that select these custom fields, you MUST defensively check if the column exists in the database first using `frappe.db.has_column(doctype, fieldname)`. This prevents hard application crashes (`MySQLdb.OperationalError: Unknown column`) in environments where the custom field has not yet been migrated or applied.