---
trigger: model_decision
description: Apply this rule when creating or modifying unit tests or test fixtures in the induct_shop app.
---

# Test Conventions Rule

When implementing unit tests or adding test coverage for new features in the `induct_shop` app, you MUST follow these guidelines.

## 1. Centralized Test Fixtures

- All master data required for tests MUST be defined in `induct_shop/tests/test_fixtures.py`.
- Never create ad-hoc master records directly inside individual test `setUp()` or `setUpClass()` methods.
- Call `test_fixtures.setup_all()` in your test `setUp()`.

**Exemption**: Pure unit tests that perform no database operations (e.g., math/logic tests) do not need `setup_all()`. Mark these clearly with a class docstring: `"""Pure unit tests — no database interaction."""`

## 2. Naming Convention

All test-generated master data MUST use the `Test ` prefix (e.g., `Test Bay 1`, `Test Tech One`, `Test Customer`, `Test SERVICE_001`). This prevents cluttering manual testing environments and allows easy filtering.

## 3. Fixed-Capacity Master Data Pool

Do NOT dynamically generate master records in loops or helper methods. Use the fixed pool provided in `test_fixtures.py`:

- **Service Bays**: `Test Bay 1` (active, Lift), `Test Bay 2` (active, Lift + Alignment Rack), `Test Bay 3` (inactive)
- **Employees**: `Test Tech One` (active), `Test Tech Two` (active), `Test Tech Three` (inactive/left)
- **Customer**: `Test Customer`
- **Repair Vehicle**: `Test VIN 01` / standard Tesla VINs (`5YJSA1E27PF123456`, `5YJYGDEE1PF123456`)
- **Items**: `Test SERVICE_001`, `Test EST_ITEM_001`, `Test EST_ITEM_002`
- **Equipment Tags**: Lift, Alignment Rack, HV Battery Station
- **Schedule Entry Types**: Diagnostic, Repair, Meeting, Maintenance / Shop Cleaning, Internal Service

## 4. Transactional Records — Classification & Lifecycle

### What is a transactional record?
A record created per test scenario that must not persist across test runs. In our domain:

| Transactional (clean up) | Master (persist via fixtures) |
|:---|:---|
| Schedule Entry | Service Bay |
| Sales Order | Customer |
| Vehicle Check-in | Employee |
| Project | Item |
| Leave Application | Equipment Tag |
| Quotation | Repair Vehicle |
| | Schedule Entry Type |
| | Shop Settings |

### Rules
- Do NOT pre-seed transactional records as permanent fixture data.
- Create transactional records on demand using helpers: `create_test_sales_order()`, `create_test_vehicle_check_in()`.
- Every test class that creates transactional records (directly or via side-effects) MUST define a `tearDown()` that calls `test_fixtures.teardown_transactional()`.

### Side-Effect Awareness
Some record insertions trigger cascading creation of other transactional records:

| Action | Side-Effect |
|:---|:---|
| Insert `Vehicle Check-in` | Auto-creates `Project` |
| Insert `Schedule Entry` with `sales_order` | Auto-populates `customer`, `project`, `repair_vehicle` from SO |
| Submit + Amend `Sales Order` | Updates linked `Schedule Entry` status to `Needs Review` |

**You MUST account for cascaded records in your tearDown.** The centralized `teardown_transactional()` handles all known cascades. If you introduce a new side-effect, update the function.

## 5. Settings Restoration

If a test mutates a singleton document (e.g., `Shop Settings`), you MUST wrap the mutation in a `try/finally` block that restores the original value:

```python
def test_capacity_toggle(self):
    doc = frappe.get_single("Shop Settings")
    original = doc.enable_technician_capacity
    try:
        doc.enable_technician_capacity = 0
        doc.save(ignore_permissions=True)
        # ... assertions ...
    finally:
        doc.enable_technician_capacity = original
        doc.save(ignore_permissions=True)
```

## 6. Test File Location

| Location | When to Use |
|:---|:---|
| `induct_shop/induct_shop/doctype/<doctype>/test_<doctype>.py` | Testing a specific DocType's controller logic (validation, hooks, auto-population). This is the Frappe convention. |
| `induct_shop/api/test_<module>.py` | Testing API-layer functions (whitelisted endpoints, business logic modules). |
| `induct_shop/tests/test_<name>.py` | Cross-cutting integration tests, pure unit tests, or tests spanning multiple DocTypes/APIs. |

## 7. Test Base Class

Use `unittest.TestCase` for all test classes. Do not use `frappe.tests.IntegrationTestCase` unless you specifically need Frappe's automatic test record loading (we use our own fixture system instead).

## 8. Valid Tesla VINs & Automatic Vehicle Decoding

- Tests MUST NOT populate vehicle attributes (`manufacturer`, `model`, `trim`, `model_year`, etc.) by hand or use dummy/invalid VIN strings (e.g., `TEST-VIN-01`, random hashes).
- Always use valid 17-character Tesla VINs provided by `test_fixtures.py` (e.g. `5YJSA1E27PF123456` for Model S Plaid, `5YJYGDEE1PF123456` for Model Y).
- Allow `RepairVehicle.before_save()` to automatically decode and set all vehicle specifications on insert.

