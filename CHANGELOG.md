# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added `before_uninstall` hook to automatically remove custom fields, property setters, and scripts injected by the app upon uninstallation.
- OKF documentation baseline and directory structure.
- Vehicle Repair DocType and functionality, including Quick Entry capabilities and server-side VIN decoding.
- Custom Link field `project` to Quotation DocType.
- Customizations to Project DocType dashboard (hidden Progress tab, reorganized connections).
- Custom costing logic for Project DocType to calculate `custom_sales_stock_cost` and `custom_incoming_material_value` from stock ledger entries, and dynamically update `expense_amount`.

### Changed
- Moved Stock Entry from Purchase section to Project section in Project DocType dashboard.
### Deprecated
### Removed
### Fixed
- Enforced the hiding of the Progress tab in Project DocType by explicitly hiding its individual field components via client script.

### Security
