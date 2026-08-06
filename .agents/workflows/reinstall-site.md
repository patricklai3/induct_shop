---
description: Reinstall Frappe site and reset database
---

Primary Directive: Use this workflow to wipe the database and cleanly reinstall the local Frappe bench site (`development.localhost`) within the Docker container environment (`devcontainer-frappe-1`).

## Workflow Steps

1. **Execute Non-Interactive Site Reinstall**
   Execute `bench reinstall` inside `devcontainer-frappe-1`, passing `--mariadb-root-password 123` and `--admin-password admin` so it executes non-interactively without prompting:
   ```bash
   docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost reinstall --yes --mariadb-root-password 123 --admin-password admin"
   ```

2. **Re-install Required Applications**
   Because `bench reinstall` resets the site database to base Frappe, install the app dependency stack back onto the site:
   ```bash
   docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost install-app erpnext hrms induct_shop"
   ```

3. **Run Site Migration**
   Apply schema updates, DocTypes, and patches for all installed applications:
   ```bash
   docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost migrate"
   ```

4. **Verify Test Suite Execution**
   Run the test suite to confirm all master records and unit tests execute cleanly on the fresh database:
   ```bash
   docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost run-tests --app induct_shop"
   ```