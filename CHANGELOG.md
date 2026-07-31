# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Integrated `frappe-ui` Vue 3 frontend stack in `frontend/` directory, including Vite 5, Tailwind CSS v3, Vue Router 4, `frappe-ui` components and semantic design tokens, with build pipeline generating static assets to `induct_shop/public/frontend` and web page route `/frontend`.
- Completed Stage 12 (Integration Testing & Edge Cases) of the Scheduling System: end-to-end verification covering full workflow, bay & technician pool capacity gating, Sales Order amendment recalculation & bay overlap warnings, leave application integration, holiday detection, lunch edge cases, equipment tag filtering, technician capacity toggling, multi-day capacity isolation, and reinstall resilience. Added comprehensive `test_stage12_integration.py` test suite (59 total tests passing).
- Tag-based Equipment Tag system (`Equipment Tag`, `Service Bay Equipment`, and `Service Equipment Requirement`) for scalable bay capability and service requirements tracking.
- Interactive equipment requirement tag chips editor in the Service & Parts Selector ingestion dialog.
- Dynamic extraction of Mobile Capable indicators from Tesla Service Manual URLs via Playwright browser automation and custom Item field `custom_is_mobile_capable`.
- Lightweight FRT-based scheduling estimation system utilizing log-normal distribution for duration predictions (Phase 1).

- Added client script to dynamically fetch customer details on Quotation when created from Project dashboard.
- Service and Parts Selector feature providing a unified modal for searching, parsing, and associating services and parts within standard transaction documents.
- Provisioned Frappe UI for Vue 3 frontend development (superseded by native implementation).
- Added Frappe UI playbooks to OKF documentation.
- Standardized OKF documentation frontmatter across all knowledge documents and relocated specifications to the standards directory.
- Vehicle Check-in workflow including `Vehicle Check-in`, `Inspection Template`, and respective child tables.
- Automated project creation triggered upon Vehicle Check-in record submission.
- Client-side intake mileage validation for `Vehicle Check-in`.
- Standard inspection template provisioning on app install.
- Added `before_uninstall` hook to automatically remove custom fields, property setters, and scripts injected by the app upon uninstallation.
- OKF documentation baseline and directory structure.
- Vehicle Repair DocType and functionality, including Quick Entry capabilities and server-side VIN decoding.
- Custom Link field `project` to Quotation DocType.
- Customizations to Project DocType dashboard (hidden Progress tab, reorganized connections).
- Custom costing logic for Project DocType to calculate `custom_sales_stock_cost` and `custom_incoming_material_value` from stock ledger entries, and dynamically update `expense_amount`.

### Changed

- Updated Scheduling System documentation (`docs/development/scheduling-system.md`) from a proposed Specification to an implemented OKF Reference document (`status: Implemented`), and added OKF Reference docs for `Schedule Entry`, `Service Bay`, and `Shop Settings`.
- Replaced binary `custom_is_mobile_capable` checkbox on Item with derived mobile capability calculated from the `custom_equipment_requirements` child table.
- Refactored the Service & Parts Selector to utilize ERPNext's native Item Variants system instead of Batches for tracking and managing part variations (revisions, conditions, and OEM statuses).
- Moved Stock Entry from Purchase section to Project section in Project DocType dashboard.

### Deprecated

### Removed

- Removed hardcoded `custom_is_mobile_capable` Check field on Item fixture.
- Removed entire legacy frontend directory and associated build configuration files in favor of Frappe UI scaffold.

### Fixed

- Fixed Service & Parts Selector item addition behavior to reuse the first empty line in the item child table before creating a new line.
- Fixed `LinkValidationError` during part ingestion in Service & Parts Selector by auto-provisioning missing `Item Attribute` records (`Revision`, `Condition`, `OEM Status`) and attribute values before template and variant item insertion.
- Recreated the `Service Part Association` and `Service Part Association Item` DocTypes as Standard DocTypes to ensure their schema persists across app reinstallations.
- Enforced the hiding of the Progress tab in Project DocType by explicitly hiding its individual field components via client script.

### Security

