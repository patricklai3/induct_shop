# Directory Update Log

## 2026-08-03
* **Update**: Refactored [Primary Vehicle Repair Workflow](/workflow.md) to position the Project as the top-level Service File container encompassing all steps (including initial diagnostic appointment scheduling) as a guided, checklist-style staff navigation experience.
* **Archive**: Relocated `scheduling-implementation-checklist.md` from `docs/development/` to `docs/archive/` and updated frontmatter to OKF specification (`type: Specification`, `status: Archived`).

## 2026-07-29
* **Fix**: Updated row insertion logic in [Service & Parts Selector](/systems/service-parts-selector.md) to reuse the first empty row (`!item_code`) in the `items` child table before creating a new line.
* **Fix**: Resolved `LinkValidationError` during part ingestion in [Service & Parts Selector](/systems/service-parts-selector.md) by dynamically auto-provisioning standard `Item Attribute` records (`Revision`, `Condition`, `OEM Status`) and their values prior to Item template/variant creation. Added `seed_item_attributes()` to app installation hooks in `install.py`.

## 2026-07-28
* **Relocation & Update**: Relocated [Scheduling System](/systems/scheduling-system.md) from `docs/development/` to `docs/systems/` and converted specification to an implemented OKF `Reference` document (`status: Implemented`).
* **Creation**: Added OKF `Reference` documentation for [Schedule Entry DocType](/doctypes/schedule-entry.md), [Service Bay DocType](/doctypes/service-bay.md), and [Shop Settings DocType](/doctypes/shop-settings.md) in `doctypes/`.
* **Update**: Completed Stage 12 of `scheduling-implementation-checklist.md` in `development`. Added `test_stage12_integration.py` covering end-to-end integration testing, capacity gating, Sales Order amendment hooks, leave integration, holiday detection, lunch edge cases, equipment tag filtering, technician capacity toggling, multi-day scheduling isolation, and reinstall resilience. All 59 tests pass.

## 2026-07-23
* **Creation**: Added `scheduling-implementation-checklist.md` in `development` to provide a 12-stage progressive build-and-verify checklist with acceptance criteria and a dependency map.

## 2026-07-22
* **Update**: Updated `scheduling-system.md` in `development` to specify the tag-based Equipment Tag system (`Service Bay Equipment` child table) and set-superset capability matching.
* **Update**: Updated `service-parts-selector.md` in `systems` to document equipment requirement tag extraction, interactive staff tag editing, and derived mobile capability.

## 2026-07-21
* **Update**: Updated `service-parts-selector.md` in `systems` to document dynamic Tesla Service Manual Mobile Capable extraction using Playwright Chromium.
* **Update**: Updated `scheduling-system.md` in `development` to reflect the architectural shift to the Phase 1 lightweight FRT log-normal estimation algorithm.

## 2026-07-09
* **Update**: Updated `quotation.md` to document the dynamic customer fetching client script.

## 2026-07-07
* **Update**: Updated `service-parts-selector.md` in `systems` to reflect the architectural shift from Batches to Item Variants for part variance tracking.

## 2026-07-06
* **Update**: Updated `service-parts-selector.md` in `systems` to reflect its completed implementation as a feature reference.

## 2026-07-02
* **Update**: Updated `vehicle-check-in.md` to reflect the completed implementation of the Vehicle Check-in DocType and Inspection Templates.

## 2026-07-01
* **Creation**: Added `vehicle-check-in.md` to `doctypes` to begin specifying the proposed Vehicle Check-in DocType features.
* **Update**: Updated `repair-vehicle.md` to document the addition of Quick Entry capabilities and the implementation of a server-side VIN decoder.

## 2026-06-30
* **Update**: Updated `project.md` to document the relocation of the "Stock Entry" item from the Purchase section to the Project section in the Project dashboard.
* **Update**: Updated `project.md` to reflect the completed implementation of custom project costing logic including new fields and automated hooks.
* **Update**: Updated `project.md` to reflect the comprehensive field-hiding mechanism required to successfully hide the Progress tab.

## 2026-06-29
* **Update**: Updated `project.md` to document the hiding of the Progress tab via custom client script.
* **Creation**: Added `project.md` to `doctypes` to document the customizations to the Project DocType dashboard.
* **Creation**: Added `quotation.md` to `doctypes` to document the addition of the Project link field to the Quotation DocType.
* **Creation**: Added [How to Clean Up Customizations on Uninstall](/playbooks/doctypes-and-db/how-to-clean-up-customizations-on-uninstall.md) playbook.

## 2026-06-27
* **Update**: Moved custom implemented `repair-vehicle.md` to `doctypes` folder.
* **Initialization**: Created foundational directory structure adhering to OKF v0.1 guidelines.
* **Creation**: Established the [Frappe Bench](/systems/frappe-bench.md) and [Installer](/scripts/installer.md) concepts.
