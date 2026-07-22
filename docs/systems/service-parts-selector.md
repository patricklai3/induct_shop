---
type: System
title: Service and Parts Selector
description: A combined service and parts selector utility accessed via sales documents.
tags: [system, ui, inventory, service-manual]
---

# Overview

A combined utility that allows users to quickly search, filter, and select both services (labor, operations) and parts (items) directly from within various documents. While primarily accessed via sales documents like Quotation, Sales Order, and Sales Invoice (where both services and parts are relevant), it also intelligently adapts to stock and procurement documents like Purchase Receipt and Stock Entry, where services (non-stock items) are not applicable.

# Goals

* Provide a unified interface for selecting services and parts.
* Improve data entry speed and accuracy for sales representatives.
* Ensure seamless integration with existing ERPNext sales documents.
* Be context-aware, automatically configuring its behavior and visibility of services/parts based on the DocType it is invoked from.

# Features

* **Unified Search:** A single search bar and integrated filtering mechanism to look up both Items (Parts) and Services.
* **Context-Aware Visibility:** Hides service-related filters, tabs, and results when opened from stock or procurement documents (e.g., Purchase Receipt, Stock Entry) since services are non-stock items.
* **Vehicle Context Filtering:** Automatically queries the vehicle information through the connected project of the doctype it is opened in, and filters available services and parts accordingly to ensure model compatibility.
* **Quick Add:** Ability to add multiple items to the sales document without closing the selector.
* **Pricing & Availability:** Displays real-time pricing and stock availability (for parts) directly in the selector.

# User Interface

* A modal interface accessible via a custom button ("Service & Parts Selector") on the Sales Document items table.

# Technical Implementation

The implementation utilizes a Frappe-native Vanilla JS / jQuery architecture to remain lightweight and fully integrated:

1. **Client Script Injection:**
   * A centralized JavaScript file (`public/js/service_parts_selector.bundle.js`).
   * Injected into standard sales and stock documents (`Quotation`, `Sales Order`, `Sales Invoice`, `Purchase Receipt`, `Stock Entry`) using the `doctype_js` hook in `hooks.py`.
2. **Custom Button:**
   * The button `"Service & Parts Selector"` is added in the `refresh` event of the targeted forms to launch the utility.
3. **User Interface (Vanilla JS in Dialog):**
   * Uses `frappe.ui.Dialog` to create the modal interface containing custom HTML fields.
   * Leverages jQuery and plain JavaScript to handle the complex state (searching, filtering, selecting items) and binds events to the DOM.
4. **Item Insertion Method:**
   * Uses the standard Frappe Client API to insert selected parts and services into the target doctypes (`Quotation`, `Sales Order`, etc.).
   * **Row Creation:** Calls `let row = frm.add_child("items");` to instantiate a new record.
   * **Triggering Native Logic:** Uses `frappe.model.set_value` to set the item code. This robust practice automatically triggers ERPNext's native field scripts (fetching prices, taxes, UOM, and descriptions).
   * **Batch Assignment:** For physical parts, explicitly links the correct condition and revision by setting `batch_no`.
   * **Service Logic:** For services, automatically sets the UOM to `Hour` and populates `qty` to ensure the correct Flat Rate Time is billed.
5. **Backend API:**
   * Whitelisted Python methods fetch services, parts, pricing, and stock.
   * Queries vehicle information from the document's connected `Project` and filters search results by `Model Compatibility`.

# Data Schema & Part Categorization

To support accurate searching, filtering, and documentation without cluttering the ERPNext database, the system utilizes the native **ERPNext Item Variants System** to manage part variances.

## Item Template vs. Variant Architecture

* **Item Master (Template Part):** The standard `Item` doctype configured as a template (`has_variants = 1`) represents the base part. It stores:
  * **Base Part Number:** The first 7 digits (e.g., `1974875`), acting as the `item_code`.
  * **Description & Categorization:** (Category, Subcategory, Group).
  * **Model Compatibility:** A custom child table mapping the base part to vehicle models and exact date ranges.
  * **Item Attributes:** Standard ERPNext Item Attributes (`Revision`, `Condition`, `OEM Status`) are attached to the template.

### Item Master Field Mapping

To ensure maximum scalability and speed within standard ERPNext workflows, the utility explicitly maps ingested data to the core `Item` fields as follows:

* **`item_code`:** The 7-digit OEM Base Part Number (for parts) or the Correction Code (for services). This ensures rapid native search, barcode scanning, and inherently prevents duplicate records.
* **`item_name`:** The short Part Name / Title (e.g., `COMPONENT - FRONT END CARRIER`).
* **`description`:** The detailed or localized description for printing on sales and inventory documents.

* **Item Variant (Specific Variance):** An `Item` doctype where `variant_of` is the template part. It tracks the specific physical variants of that base part via standard `Item Variant Attribute` rows:
  * **Revision:** Attribute value (e.g., `-00-C`).
  * **Condition:** Attribute value with standard options (`New`, `Reconditioned`, `Used`).
  * **OEM Status:** Attribute value with standard options (`OEM`, `Aftermarket`).
  * **Smart Variant ID Generation:** The ingestion system automatically generates a structured Variant ID format for the `item_code`: `#######-##-X-XXX-XXX` (e.g., `1234567-00-D-AFT-NEW`).

## Installation & Configuration Requirements

To ensure the accounting engine correctly differentiates the cost and valuation, **Batch-wise Valuation** must be enforced globally.

* The `induct_shop` app programmatically enables the "Use batch-wise valuation" toggle within ERPNext's `Stock Settings` upon app installation.

## Categorization Hierarchy & Item Group Generation

The utility automatically configures ERPNext's standard `Item Group` hierarchy during ingestion.

* **Dynamic Tree Generation:** Verifies and dynamically generates an `Item Group` tree structured as: `Make` -> `Category` -> `Subcategory` -> `Group`.
* **Model Exclusion:** Vehicle models are explicitly excluded from this Item Group tree to prevent massive structural duplication. Model compatibility remains exclusively managed by the custom child table on the Item.

# Part Ingestion Workflow

Parts are ingested incrementally ("just-in-time") as they are encountered and needed for documents.

## User Workflow & Parsing

* When a part is needed, the user enters a search term into the utility.
* The utility automatically generates a link to the Tesla Parts Catalog.
* The user navigates to the catalog, copies the tabulated part information, and pastes it into a dedicated ingestion field in the utility.
* **Automated Parsing:** The utility parses the pasted text (typically tab-delimited) to extract and map: Base Part Number, Revision, Description, Localized Description, Model Compatibility, Category, Subcategory, and Group.
* **Multi-Model Deduplication Logic:** Intelligently aggregates rows that differ only by compatible vehicle models, appending distinct models to the `Model Compatibility` child table without creating redundant items.

# Service Ingestion Workflow

Service operations (labor) are ingested by parsing links directly from the Tesla Service Manual.

## User Workflow & Extraction

1. **Contextual Manual Link:** The utility provides a quick-access link to the specific Tesla Service Manual corresponding to the vehicle model and year linked to the active document.
2. **URL Input Field:** The user navigates the manual, copies the URL for the desired service, and pastes it into the utility.
3. **Automated Parsing:** The backend parses the link to extract: Title, Correction Code, FRT Value, Compatible Model, and derives the Categorization Mapping based on the Correction Code structure.
4. **Equipment Requirement Extraction & Interactive Staff Overrides:** Uses Playwright browser automation with a "Wait and Locate" strategy on `p.shortdesc .mobile-capable-indicator` to verify dynamic client-side DOM injection. If the manual indicates "Not Mobile Capable", the system defaults to populating a "Lift" equipment requirement tag. Staff are presented with an interactive tag modal during ingestion to add, edit, or remove required equipment tags (e.g. "Lift", "Alignment Rack") before saving.

## Data Schema & Deduplication

* **Correction Code as Identifier:** The `Correction Code` acts as a unique identifier for services.
* **Smart Insertion/Retrieval:** When a URL is submitted, the system retrieves the existing service record or creates a new one.
* **Model Context:** The service record tracks the specific vehicle models it applies to, dynamically expanding as it is ingested from different model manuals over time.
* **Equipment Requirements & Derived Mobile Capability:** Equipment requirements are tracked in the `custom_equipment_requirements` child table (`Service Equipment Requirement`). A service with no equipment requirements is inherently mobile capable.

# Service & Parts Association

To streamline workflows, the utility learns and associates services with the parts they require.

## Relational Linking

* When a user groups a service and part(s) together on a document, the system records an association between that Service and those Part(s).
* **One-to-Many Logic:** The association schema links one service to multiple distinct parts.

## Smart Suggestions

* Once an association is established, future selections of that service within the utility proactively suggest the linked parts to the user, accelerating data entry.

## Document Row Grouping (Print Provision)

* **Data Provision:** A custom field (`custom_parent_service_reference`) on standard transaction child tables (`Sales Order Item`, etc.) is populated automatically when adding associated parts, ensuring future custom print formats can seamlessly group and nest parts under their respective correction codes.
