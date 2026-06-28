---
type: Specification
title: Service and Parts Selector
description: Specifications for a combined service and parts selector utility accessed via sales documents.
tags: [feature, ui, inventory]
---

# Overview

A combined utility that allows users to quickly search, filter, and select both services (labor, operations) and parts (items) directly from within various documents. While primarily accessed via sales documents like Quotation, Sales Order, and Sales Invoice (where both services and parts are relevant), it must also intelligently adapt to stock and procurement documents like Purchase Receipt and Stock Entry, where services (non-stock items) are not applicable.

# Goals

* Provide a unified interface for selecting services and parts.
* Improve data entry speed and accuracy for sales representatives.
* Ensure seamless integration with existing ERPNext sales documents.
* Be context-aware, automatically configuring its behavior and visibility of services/parts based on the DocType it is invoked from.

# Features

* **Unified Search:** A single search bar or integrated filtering mechanism to look up both Items (Parts) and Services.
* **Context-Aware Visibility:** Hide service-related filters, tabs, and results when opened from stock or procurement documents (e.g., Purchase Receipt, Stock Entry) since services are non-stock items.
* **Quick Add:** Ability to add multiple items to the sales document without closing the selector.
* **Pricing & Availability:** Display real-time pricing and stock availability (for parts) directly in the selector.

# User Interface

* A modal or a slide-out panel accessible via a custom button on the Sales Document items table.

# Technical Implementation

Based on Frappe development playbooks, the proper way to implement this is:

1. **Client Script Injection:**
   * Create a centralized JavaScript file (e.g., `public/js/service_parts_selector.bundle.js`).
   * Inject this script into standard sales and stock documents (`Quotation`, `Sales Order`, `Sales Invoice`, `Purchase Receipt`, `Stock Entry`) using the `doctype_js` hook in `hooks.py`.
2. **Custom Button:**
   * Use `frm.add_custom_button(__('Service & Parts Selector'), function() { ... }, __('Utilities'))` in the `refresh` event of the targeted forms to launch the utility.
3. **User Interface (Vue 3 in Dialog):**
   * Use `frappe.ui.Dialog` to create a modal interface containing a custom HTML field.
   * Create a Vue 3 Single File Component (`.vue`) to handle the complex state (searching, filtering, selecting items) and mount it into the Dialog's HTML wrapper.
4. **Item Insertion Method:**
   * To insert selected parts and services into the target doctypes (`Quotation`, `Sales Order`, etc.) robustly, the utility will utilize the standard Frappe Client API.
   * **Row Creation:** It will call `let row = frm.add_child("items");` to instantiate a new record in the document's items table.
   * **Triggering Native Logic:** It will use `frappe.model.set_value(row.doctype, row.name, 'item_code', selected_item_code);` to set the item. Using `set_value` instead of direct assignment is a crucial, robust practice because it automatically triggers ERPNext's native field scripts (fetching prices, taxes, UOM, and descriptions).
   * **Batch Assignment:** For physical parts, it will subsequently call `frappe.model.set_value(row.doctype, row.name, 'batch_no', selected_batch_no);` to explicitly link the correct condition and revision.
   * **Service Logic:** For services, the utility will automatically set the UOM to `Hour` and call `frappe.model.set_value(row.doctype, row.name, 'qty', frt_value);` to ensure the correct Flat Rate Time is billed.
5. **Backend API:**
   * Whitelisted Python methods to fetch services, parts, pricing, and stock.

# Data Schema & Part Categorization

To support accurate searching, filtering, and documentation without cluttering the ERPNext database, the system will utilize the native **ERPNext Batch System** to manage part variances.

## Item vs. Batch Architecture
* **Item Master (Base Part):** The standard `Item` doctype will represent the base part. It will store:
  * **Base Part Number:** The first 7 digits (e.g., `1974875`), acting as the `item_code`.
  * **Description & Categorization:** (Category, Subcategory, Group).
  * **Model Compatibility:** A custom child table mapping the base part to vehicle models and exact date ranges.
  * **Batch Configuration:** The native `has_batch_no` property must be checked by default for ingested parts. Native `has_serial_no` must be left unchecked to prevent strict operational blocking.

### Optional Serial Number Registry
To track high-value or scanned parts (like HV batteries or data matrices) without enforcing ERPNext's rigid native rules (which would block transactions if an aftermarket variant lacks a serial), the system utilizes a custom, non-blocking registry.
* **Component Serial Record:** A custom doctype acts as a centralized ledger tracking the `Serial Number`, `Item`, `Batch`, `Status` (e.g., In Stock, Installed), and a dynamic link to the specific `Transaction Document` (e.g., Purchase Receipt, Sales Invoice) that spawned the current status.
* **Frictionless Workflow:** Standard transaction item tables (e.g., `Purchase Receipt Item`, `Sales Invoice Item`) will include a custom `Scanned Serial Numbers` field. Technicians can optionally scan serials into this field. Background scripts will automatically create or update the `Component Serial Record` upon submission, never halting the transaction if left blank.

### Item Master Field Mapping
To ensure maximum scalability and speed within standard ERPNext workflows, the utility explicitly maps ingested data to the core `Item` fields as follows:
* **`item_code`:** The 7-digit OEM Base Part Number (for parts) or the Correction Code (for services). This ensures rapid native search, barcode scanning, and inherently prevents duplicate records.
* **`item_name`:** The short Part Name / Title (e.g., `COMPONENT - FRONT END CARRIER`).
* **`description`:** The detailed or localized description for printing on sales and inventory documents.

* **Batch Master (Specific Variance):** The `Batch` doctype will track the specific physical variants of that base part. We will inject custom fields into the `Batch` doctype via the app to store:
  * **Revision / Suffix:** (e.g., `-00-C`). This is crucial for inventory tracking and explicit documentation on sales invoices.
  * **Condition:** `New`, `Reconditioned`, `Used`.
  * **OEM Status:** `OEM`, `Aftermarket`.

This architecture ensures the Item master remains clean (one record per base component), while the stock ledger natively tracks quantities and values at the exact revision and condition level via Batches.

## Installation & Configuration Requirements
To ensure the accounting engine correctly differentiates the cost and valuation of a "Used" part versus a "New" part (which share the same base Item Code but reside in different Batches), **Batch-wise Valuation** must be enforced globally.
* The `induct_shop` app must programmatically enable the "Use batch-wise valuation" toggle within ERPNext's `Stock Settings` upon app installation (e.g., via the `after_install` hook).

## Categorization Hierarchy & Item Group Generation
The utility must automatically configure ERPNext's standard `Item Group` hierarchy during ingestion. 
* **Dynamic Tree Generation:** When a part or service is ingested, the system will verify and dynamically generate (if missing) an `Item Group` tree structured as: `Make` (e.g., Tesla) -> `Category` -> `Subcategory` -> `Group`.
* **Example Path:** `Tesla` -> `10 - BODY` -> `1001 - Bumper and Fascia` -> `Front Bumper Carrier`.
* **Item Assignment:** The newly created part will be assigned directly to the leaf node (e.g., `Front Bumper Carrier`).
* **Model Exclusion:** Vehicle models are explicitly excluded from this Item Group tree to prevent massive structural duplication, as one part can be compatible with multiple models. Model compatibility remains exclusively managed by the custom child table on the Item.

# Part Ingestion Workflow

Just like services, the system will not crawl or pre-populate the database with the entire Tesla parts catalog. Parts will be ingested incrementally ("just-in-time") as they are encountered and needed for documents.

## User Workflow & Parsing
* When a part is needed but not found in the database, the user enters a search term into the utility.
* The utility automatically generates and provides a link to the Tesla Parts Catalog (e.g., `https://parts.tesla.com/en-US/find-part?searchTerm=[search_term]`).
* The user navigates to this link, copies the tabulated part information directly from the catalog, and pastes it into a dedicated ingestion field in the utility.
* **Automated Parsing:** The utility must parse the pasted text (typically tab-delimited). A standard row of input looks like:
  `1974875-00-C    COMPONENT - FRONT END CARRIER        Model Y Feb 2025    10 - BODY    1001 - Bumper and Fascia    Front Bumper Carrier`
* The parser will extract and map: Base Part Number, Revision, Description, Localized Description, Model Compatibility, Category, Subcategory, and Group.
* **Multi-Model Deduplication Logic:** Frequently, pasted inputs will contain multiple rows for the exact same part number that differ only by the compatible vehicle model (e.g., one row for `Model Y`, one for `Model 3`). The ingestion logic must intelligently aggregate these rows. Instead of throwing a duplication error or creating redundant items, it will append all distinct models into the `Model Compatibility` child table of that single Base Part record.
* Once parsed and aggregated, the user confirms the details, selects the Condition and OEM Status, and the system saves the new part (Item and Batch) to the database.

# Service Ingestion Workflow

To handle the ingestion and selection of service operations (labor), the utility relies on parsing links directly from the Tesla Service Manual.

## User Workflow & Extraction
1. **Contextual Manual Link:** The utility provides a quick-access link to the specific Tesla Service Manual corresponding to the vehicle model and year linked to the active document.
2. **URL Input Field:** The user navigates the online manual, copies the URL for the desired service, and pastes it into an input field within the selector utility.
3. **Automated Parsing:** The backend parses the provided link to extract three crucial pieces of information:
   * **Title:** (e.g., `Bracket - Active Hood Strut - LH (Remove and Replace)`)
   * **Correction Code:** (e.g., `11330012`)
   * **FRT Value:** (e.g., `0.42`)
   * **Compatible Model:** unlike parts this can be accurate to the year
   * **Categorization Mapping:** The system automatically derives the service hierarchy from the Correction Code:
     * **Category:** Identified by the first 2 digits of the code.
     * **Subcategory:** Identified by the first 4 digits of the code.

## Data Schema & Deduplication
* **Correction Code as Identifier:** A single correction code may apply to multiple vehicle models. To prevent database bloat and cluttered records, the `Correction Code` acts as a unique identifier for services.
* **Smart Insertion/Retrieval:** When a URL is submitted:
  * The system searches the database for an existing service record with that `Correction Code`.
  * If a match is found, the existing record is returned and added to the sales document.
  * If no match is found, a new service record is created using the extracted Title, Correction Code, FRT, and derived Category/Subcategory, and is then added to the document.
* **Model Context:** Just like parts, services must track model compatibility. The service record should be capable of tracking the specific vehicle models it applies to, dynamically expanding this list as the service is ingested from different model manuals over time.

# Service & Parts Association

To streamline repetitive workflows, the utility must intelligently learn and associate services with the parts they require.

## Relational Linking
* Most services (e.g., removing and replacing a component) inherently require one or more physical parts.
* The system must capture these relationships. When a user groups a service and part(s) together on a document for the first time, the system should record an association between that Service (Correction Code) and those Part(s).
* **One-to-Many Logic:** The association schema must be robust enough to link one service to multiple distinct parts, as complex repairs often require a primary component alongside various clips, brackets, or bolts.

## Smart Suggestions
* Once an association is established in the database, future selections of that service within the utility should proactively suggest the linked parts to the user.
* This dramatically accelerates data entry and ensures technicians or sales reps do not forget necessary ancillary components when quoting or billing a job.

## Document Row Grouping (Print Provision)
While the utility manages searching and associating parts, it must also provision data on the transaction document to support future nested printing features (where parts visually nest under the specific labor operation).
* **Service as a Parent:** When a user selects parts that are associated with a specific service via the utility, those part rows inserted into the ERPNext document must contain a relational link to that specific service row.
* **Data Provision:** A custom field (e.g., `Parent Service Reference` or `Job Group ID`) must be injected into the standard transaction child tables (e.g., `Sales Order Item`, `Sales Invoice Item`). The utility will populate this field automatically when adding associated parts, ensuring future custom print formats can seamlessly group and nest parts under their respective correction codes.
