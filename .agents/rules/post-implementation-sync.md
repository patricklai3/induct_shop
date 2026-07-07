---
trigger: model_decision
description: Apply this rule after implementing a feature, modifying DocTypes, or making backend changes in the induct_shop app.
---

# Post-Implementation Fast Sync Rule

Immediately after you complete the implementation of a feature, modify a DocType, or make backend schema changes within the `induct_shop` app, you MUST run the following command to sync the changes so the user can test them manually:

```bash
bench execute induct_shop.utilities.fast_sync.run
```

Ensure this command is executed from the `/workspace/development/frappe-bench` directory.
