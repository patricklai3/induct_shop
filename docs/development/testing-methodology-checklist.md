---
type: Specification
title: "Testing Methodology Improvement Checklist"
description: "Staged development checklist tracking transactional leak fixes, fixture migration, ingestion test conversion, test documentation, and architectural improvements."
status: Active
tags: [checklist, testing, fixtures, development, tracking]
timestamp: 2026-08-06T00:00:00Z
---

# Testing Methodology Improvement Checklist

This checklist tracks the staged implementation of testing methodology improvements for `induct_shop`, as specified in [testing-methodology-spec.md](./testing-methodology-spec.md).

---

## Stage 1: Expand `test_fixtures.py` Infrastructure & Prefix Migration

- [x] **1.1 Migrate `PREFIX` constant from `_IST_` to `Test `**:
  - Change `PREFIX = "_IST_"` to `PREFIX = "Test "` in `test_fixtures.py`.
  - Rename all master data constants (e.g., `_IST_Bay 1` → `Test Bay 1`, `_IST_Customer` → `Test Customer`).
  - Update all test files that import `PREFIX` from `test_fixtures` — string references will automatically resolve via the constant.
  - Delete any old `_IST_*` master data records left over in the database.

- [x] **1.2 Overhaul `.agents/rules/test-conventions.md`**:
  - Replace the current 4-bullet-point rule with the comprehensive 7-section version specified in [testing-methodology-spec.md Section 6.2](./testing-methodology-spec.md).
  - Key additions beyond the prefix rename:
    - Add explicit master vs transactional DocType classification table (6 transactional types).
    - Add side-effect / cascade awareness section (VCI → Project, SE auto-population from SO).
    - Add mandatory `tearDown()` enforcement with pure unit test exemption criteria.
    - Add settings restoration pattern (`try/finally`) with code example.
    - Add test file location decision table (DocType dir vs API dir vs tests dir).
    - Add test base class guidance (`unittest.TestCase` standard).
    - Add complete fixture pool inventory listing all master data records.

- [x] **1.3 Add valid Tesla VIN Repair Vehicles to master data pool**:
  - Add `REPAIR_VEHICLE_MODEL_S` (`5YJSA1E27PF123456`) and `REPAIR_VEHICLE_MODEL_Y` (`5YJYGDEE1PF123456`) dict constants to `test_fixtures.py`.
  - Add `ensure_repair_vehicles()` function that inserts `Repair Vehicle` with valid 17-character VINs and lets `RepairVehicle.before_save()` automatically decode all vehicle specifications (`manufacturer`, `model`, `trim`, `model_year`, `drivetrain`, `battery_type`, etc.) — zero manual field assignment.
  - Add call to `ensure_repair_vehicles()` inside `setup_all()`.

- [x] **1.4 Expand `teardown_transactional()` scope**:
  - Add `Vehicle Check-in` cleanup (filter: `customer LIKE 'Test %' OR customer LIKE '_Test%'`).
  - Add `Project` cleanup (filter: `customer LIKE 'Test %' OR customer LIKE '_Test%'`).
  - Add `Repair Vehicle` cleanup for ad-hoc test VINs (filter: `name LIKE 'TESTVIN%'`).
  - Ensure FK-safe deletion order: VCI → SE → Project → SO → Leave Application.

- [x] **1.5 Add `create_test_vehicle_check_in()` helper**:
  - Create helper function accepting optional `customer`, `vehicle`, and `schedule_entry` params.
  - Default to `Test Customer` and `5YJSA1E27PF123456`.

### Stage 1 Acceptance Criteria
- **Automated Testing Criteria**:
  - `setup_all()` returns `emp_map` and `5YJSA1E27PF123456` exists in DB with automatically decoded specifications (`is_valid_vin = 1`, `model = "Model S"`, `trim = "Plaid"`).
  - `teardown_transactional()` cleans all 5 transactional DocTypes with zero residual `Test %` or `_Test%` records.
  - No `_IST_*` prefixed records remain in the database.
- **Manual Verification**:
  - Run `bench run-tests --app induct_shop` — all existing tests still pass (backward-compatible expansion).
  - `.agents/rules/test-conventions.md` reflects the new `Test ` prefix and valid VIN rules.

---

## Stage 2: Migrate `test_vehicle_check_in.py`

- [x] **2.1 Replace `setUpClass` master data with `test_fixtures.setup_all()`**:
  - Remove inline creation of `_Test Checkin Customer`, `TEST-VIN-VCI-01`, `_Test Checkin Bay`.
  - Remove manual vehicle attribute assignments (`manufacturer`, `model`, `trim`).
  - Replace with `setUp()` calling `test_fixtures.setup_all()`.
  - Update all test references: `_Test Checkin Customer` → `Test Customer`, `_Test Checkin Bay` → `Test Bay 1`, `TEST-VIN-VCI-01` → `5YJSA1E27PF123456` (valid Model S VIN).

- [x] **2.2 Add proper `tearDown()` with full cleanup**:
  - Call `test_fixtures.teardown_transactional()` to clean VCI, Project, SE, and SO records.

- [x] **2.3 Verify all 3 test methods pass unchanged**:
  - `test_schedule_entry_cross_linking`
  - `test_vehicle_checkin_project_creation_naming`
  - `test_duplicate_vehicle_checkin_same_customer_car`

### Stage 2 Acceptance Criteria
- **Automated Testing Criteria**:
  - All 3 Vehicle Check-in tests pass.
  - After test run, `SELECT count(*) FROM \`tabVehicle Check-in\` WHERE customer LIKE 'Test %' OR customer LIKE '_Test%'` returns `0`.
  - After test run, `SELECT count(*) FROM \`tabProject\` WHERE customer LIKE 'Test %' OR customer LIKE '_Test%'` returns `0`.

---

## Stage 3: Migrate `test_schedule_entry.py`

- [ ] **3.1 Replace 91-line ad-hoc `setUp()` with `test_fixtures.setup_all()`**:
  - Remove inline creation of `_Test Schedule Customer`, `Test Schedule Bay`, `_Test Service Item 01`, `TEST-VIN-SCHED-01`, `_Test Schedule Project`, and Sales Order.
  - Remove manual vehicle attribute assignments.
  - Replace with `setUp()` calling `test_fixtures.setup_all()` + `create_test_sales_order()`.
  - Update all test references to use `Test *` pool records and valid VIN `5YJSA1E27PF123456`.

- [ ] **3.2 Add proper `tearDown()` with full cleanup**:
  - Call `test_fixtures.teardown_transactional()` to clean all transactional records including cross-DocType VCI and Project entries.

- [ ] **3.3 Verify all 10 test methods pass unchanged**:
  - `test_schedule_entry_auto_population`
  - `test_so_line_frt_override`
  - `test_duplicate_sales_order_blocked`
  - `test_status_transitions`
  - `test_standalone_schedule_entry_creation`
  - `test_standalone_capacity_conflict`
  - `test_display_helper_fallbacks`
  - `test_schedule_entry_type_records`
  - `test_vehicle_check_in_linkage`
  - `test_repair_entry_with_sales_order`

### Stage 3 Acceptance Criteria
- **Automated Testing Criteria**:
  - All 10 Schedule Entry tests pass.
  - Zero ad-hoc `_Test Schedule*` or `Test Schedule Bay` records remain after teardown.
  - All references use `Test ` prefix constants and valid Tesla VINs.
  - `setUp()` is ≤ 15 lines (down from 91).

---

## Stage 4: Fix `test_scheduling_views.py` Leak & Migrate to Valid VINs

- [ ] **4.1 Migrate `test_resolve_vehicle_info_with_model_formatting` to valid Tesla VIN**:
  - Remove fake hash VIN and manual vehicle field assignments (`model_year="2023"`, `model="Model Y"`, `trim="Long Range"`).
  - Use valid Tesla Model Y VIN `5YJYGDEE1PF123456` and rely on `RepairVehicle.before_save()` automatic decoding.

- [ ] **4.2 Verify expanded `teardown_transactional()` coverage**:
  - Confirm Repair Vehicle and Project created in test are cleaned by `teardown_transactional()`.

### Stage 4 Acceptance Criteria
- **Automated Testing Criteria**:
  - All 5 scheduling views tests pass.
  - `SELECT count(*) FROM \`tabRepair Vehicle\` WHERE name LIKE 'TESTVIN%'` returns `0` after run.
  - `SELECT count(*) FROM \`tabProject\` WHERE name LIKE 'Project TESTVIN%'` returns `0` after run.

---

## Stage 5: Convert `run_ingestion_test.py` to Proper Unit Test

- [ ] **5.1 Rename and restructure**:
  - Rename file from `run_ingestion_test.py` to `test_ingestion.py`.
  - Replace manual `run_tests()` function with standard `unittest.TestCase` class.

- [ ] **5.2 Implement `test_ingest_part()` method**:
  - Call `ingest_part()` with the existing `TEST_PARTS` constant.
  - Assert expected Items are created (e.g., `1083401`, `2188359-10-B`, `2188354-10-B`).
  - Assert deduplication: `1083401` has exactly 2 model compatibility entries (Model 3, Model Y).

- [ ] **5.3 Implement `test_ingest_service()` method with mocked HTTP**:
  - Use `unittest.mock.patch` to mock the HTTP response from `service.tesla.com`.
  - Assert service item is ingested correctly without making external network calls.

- [ ] **5.4 Add proper `setUp()` and `tearDown()`**:
  - `setUp()` calls `test_fixtures.setup_all()`.
  - `tearDown()` cleans up any Items created during tests (filter by known test item codes).

### Stage 5 Acceptance Criteria
- **Automated Testing Criteria**:
  - `bench run-tests --module induct_shop.tests.test_ingestion` discovers and runs all test methods.
  - No external HTTP calls are made during test execution.
  - All assertions pass.

---

## Stage 6: Create Testing Documentation

- [ ] **6.1 Create `docs/systems/testing-suite.md`**:
  - Add OKF frontmatter (`type: Reference`).
  - Include architecture diagram (Mermaid) showing test file → fixture → API/DocType dependency graph.
  - Include complete test suite inventory table (all files, classes, methods, categories).
  - Document fixture system: master pool, transactional helpers, `Test ` prefix convention.
  - Document valid VIN seeding rule and automatic vehicle decoding.
  - Document Docker-specific test execution commands.
  - Document `setUp`/`tearDown` transactional hygiene contract.

- [ ] **6.2 Update `docs/index.md`**:
  - Add link to `docs/systems/testing-suite.md` under `# Systems`.

### Stage 6 Acceptance Criteria
- **Automated Testing Criteria**:
  - All docs pass OKF validation (valid YAML frontmatter, valid tags, no broken links).
- **Manual Review Criteria**:
  - Review Mermaid architecture diagram renders correctly.
  - Review test inventory table is complete and accurate.

---

## Stage 7: Full Suite Verification & Cleanup

- [ ] **7.1 Run full test suite**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench && bench --site development.localhost run-tests --app induct_shop"
  ```

- [ ] **7.2 Run suite twice consecutively** to verify no data leaks between runs:
  - First run: all tests pass.
  - Second run: all tests pass with identical results (no accumulated test data).

- [ ] **7.3 Verify zero residual test data** after final run:
  ```sql
  SELECT count(*) FROM `tabVehicle Check-in` WHERE customer LIKE 'Test %' OR customer LIKE '_Test%';
  SELECT count(*) FROM `tabProject` WHERE customer LIKE 'Test %' OR customer LIKE '_Test%';
  SELECT count(*) FROM `tabSchedule Entry` WHERE service_bay LIKE 'Test %' OR service_bay LIKE '_Test%' OR service_bay = 'Test Schedule Bay';
  SELECT count(*) FROM `tabSales Order` WHERE customer LIKE 'Test %' OR customer LIKE '_Test%';
  ```
  All queries must return `0`.

### Stage 7 Acceptance Criteria
- **Automated Testing Criteria**:
  - Docker command `bench --site development.localhost run-tests --app induct_shop` completes with 100% pass rate on two consecutive runs.
  - Zero residual test data in all transactional DocTypes.
