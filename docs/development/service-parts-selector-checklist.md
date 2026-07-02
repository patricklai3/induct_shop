# Staged Implementation Plan: Service & Parts Selector

## Phase 1: Data Schema & Core Backend Setup
- [x] Modify `Item` DocType via Custom Fields (or standard properties):
  - Add `Model Compatibility` (Child Table: Model, Date Range).
  - Ensure `has_batch_no` is checked by default for ingested parts.
- [x] Modify `Batch` DocType:
  - Add Custom Field `Revision / Suffix` (e.g., `-00-C`).
  - Add Custom Field `Condition` (`New`, `Reconditioned`, `Used`).
  - Add Custom Field `OEM Status` (`OEM`, `Aftermarket`).
  - Implement `autoname` hook to automatically generate the Batch ID in the format `#######-##-X-XXX-XXX` (e.g., `1234567-00-D-AFT-NEW` or `1234567-00-D-OEM-USD`), combining Item Code, Revision, OEM Status, and Condition.
- [x] Implement `after_install` hook (or patch) to automatically enable "Use batch-wise valuation" in Stock Settings.
- [x] Add Custom Field `Parent Service Reference` (or `Job Group ID`) to Transaction Item Tables for relational grouping.

## Phase 2: Data Ingestion & API Logic (Python Backend)
- [ ] Implement Part Ingestion Logic (Tesla Catalog Text Parser):
  - Parse tab-delimited text for Base Part Number, Revision, Description, Localized Description, Model Compatibility, Category, Subcategory, Group.
  - Dynamically generate `Item Group` tree (`Make` -> `Category` -> `Subcategory` -> `Group`).
  - Deduplicate models and intelligently append to the `Model Compatibility` child table.
  - Create/Update `Item` and `Batch` records.
- [ ] Implement Service Ingestion Logic (Tesla Manual URL Parser):
  - Parse service manual URL to extract Title, Correction Code, FRT Value, Compatible Model.
  - Generate Service Record (using Correction Code as unique identifier).
- [ ] Implement Service & Parts Association Logic:
  - Background logic to record relational links when services and parts are grouped together on a document.
- [ ] Create Whitelisted API endpoints:
  - Fetching services & parts (with pricing/stock).
  - Processing part/service ingestion payloads.
  - Fetching smart part suggestions based on a given service.

## Phase 3: Frontend UI Components (Vue 3)
- [ ] Setup `public/js/service_parts_selector.bundle.js` build configuration.
- [ ] Create Vue 3 Single File Component (`.vue`) for the Dialog/Modal interface.
- [ ] Implement Unified Search UI to query both Items (Parts) and Services.
- [ ] Implement Context-Aware logic to dynamically hide service-related filters/results when opened from stock/procurement docs (e.g., Purchase Receipt).
- [ ] Implement UI for real-time pricing and stock availability display.
- [ ] Implement Smart Suggestions UI to prompt users with parts associated with their selected services.
- [ ] Implement Ingestion Forms/Inputs within the modal (URL input for services, Text area for parts) to trigger the backend ingestion APIs.

## Phase 4: Frappe Client Integration (ERPNext Standard Docs)
- [ ] Inject `service_parts_selector.bundle.js` into targeted DocTypes (`Quotation`, `Sales Order`, `Sales Invoice`, `Purchase Receipt`, `Stock Entry`) via `doctype_js` in `hooks.py`.
- [ ] Add a custom button `"Service & Parts Selector"` to the items table in targeted forms (using `frm.add_custom_button`).
- [ ] Implement Item Insertion Logic (JavaScript) to push selections back to the ERPNext document:
  - Call `frm.add_child("items")` to instantiate new rows.
  - Use `frappe.model.set_value` to set `item_code` (crucial to trigger native Frappe fetch scripts for price/tax/uom).
  - Explicitly set `batch_no` for parts.
  - Set `qty` (FRT value) and UOM (`Hour`) for services.
  - Populate the `Parent Service Reference` field to ensure parts visually nest under services for future print formats.
