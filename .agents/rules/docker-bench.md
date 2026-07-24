---
trigger: always_on
description: Apply this rule when running bench, frappe, or environment commands to execute them inside the Docker container.
---

# Docker Bench Command Execution Rule

The bench environment and Frappe application run inside a Docker container (`devcontainer-frappe-1`).

When executing any `bench` commands (e.g., `bench execute`, `bench migrate`, `bench build`, `bench reinstall`, etc.), you MUST execute them inside the Docker container using `docker exec`.

## Command Format

All `bench` commands must start with:

```bash
docker exec -it devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && <command>"
```

*(Note: Use `-i` without `-t` for non-interactive commands in scripts if pseudo-TTY allocation is not needed).*

## Common Examples

- **Fast Sync**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench execute induct_shop.utilities.fast_sync.run"
  ```

- **Migrate**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench migrate"
  ```

- **Run App Tests**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost run-tests --app induct_shop"
  ```
