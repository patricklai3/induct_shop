---
trigger: model_decision
description: Apply this rule after implementing a feature, modifying DocTypes, or making backend changes in the induct_shop app.
---

# Post-Implementation Fast Sync Rule

Immediately after you complete the implementation of a feature, modify a DocType, or make backend schema changes within the `induct_shop` app, you MUST run the following command to sync the changes so the user can test them manually:

```bash
docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench execute induct_shop.utilities.fast_sync.run"
```
