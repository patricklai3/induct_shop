---
trigger: model_decision
description: Apply this rule when creating or modifying features to ensure all feature requests are handled within the induct shop directory.
---

# Feature Requests Rule

All feature requests must be accomplished within the `induct shop` directory. When implementing new features, components, or enhancements, ensure that the code is placed and modified inside the `induct shop` application or directory structure, rather than in generic workspace folders or other apps, unless explicitly specified otherwise by the user.

Furthermore, all features must be available upon reinstall. This means they cannot be achieved through commands that insert doctype customizations directly into the database; instead, they must be committed to the application codebase as standard fixtures or schema definitions.