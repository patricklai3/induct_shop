---
trigger: model_decision
description: Apply this rule when creating or modifying unit tests or test fixtures in the induct_shop app.
---

# Test Data & Fixtures Rule

When implementing unit tests or adding test coverage for new features in the `induct_shop` app, you MUST follow these guidelines:

1. **Use Centralized Test Fixtures**:
   - All master data required for tests (Service Bays, Equipment Tags, Customers, Employees, Items, etc.) MUST be defined in `induct_shop/tests/test_fixtures.py`.
   - Never create ad-hoc master records directly inside individual test file `setUp()` methods.
   - Call `test_fixtures.setup_all()` in your test `setUp()`.

2. **Master Data Naming Convention**:
   - All test-generated master data MUST use the `_IST_` prefix (e.g., `_IST_Bay 1`, `_IST_Tech One`, `_IST_Customer`, `_IST_SERVICE_001`).
   - This prevents cluttering manual testing environments and allows easy filtering and identification.

3. **No Unbounded Pool Expansion**:
   - Do NOT dynamically generate master records (e.g., creating "Test Bay Pool 1, 2, 3...") in loops or helper methods.
   - Use the fixed-capacity pool provided in `test_fixtures.py` (`_IST_Bay 1`, `_IST_Bay 2`, `_IST_Bay 3`, active technicians `_IST_Tech One`, `_IST_Tech Two`, inactive `_IST_Tech Three`).

4. **Transactional Records vs Master Records**:
   - Do NOT pre-seed transactional records (e.g., Sales Orders, Schedule Entries) as permanent master data.
   - Create transactional records on demand using helper methods like `test_fixtures.create_test_sales_order()`.
   - Always call `test_fixtures.teardown_transactional()` in `tearDown()` to clean up transactional entries (Schedule Entries, Leave Applications, Sales Orders) created during tests.
