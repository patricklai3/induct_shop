---
type: Reference
title: "Repair Vehicle DocType"
description: Documentation for the Repair Vehicle DocType and its integrated Tesla VIN Decoder.
tags: [frappe, development, doctype, feature]
timestamp: 2026-06-27T08:37:00Z
---

# Repair Vehicle DocType

The `Repair Vehicle` DocType is designed to keep a detailed record of Tesla vehicles being serviced within the Induct Shop application.

## Core Features

- **Quick Entry Integration**: The DocType supports Quick Entry (`quick_entry: 1`). The dialog exposes editable fields including `customer`, `license_plate`, `color`, `vin`, and `manufactured_month`.
- **Tesla VIN Decoder**: This DocType includes a dual-layered VIN decoder (client-side JS for instant feedback, and server-side Python `before_save` hook for data integrity during Quick Entry and API creation). When a 17-character Tesla VIN is entered, it automatically decodes the VIN and populates the standard Read Only fields.
- **Data Extracted**:
  - `manufacturer`: e.g. Tesla Fremont, CA
  - `model`: e.g. Model 3, Model Y
  - `model_year`: e.g. 2022
  - `body_type`: e.g. Sedan 4-Door
  - `trim`: e.g. Long Range
  - `drivetrain`: e.g. AWD
  - `battery_type`: e.g. LFP
  - `drive_unit`: e.g. Dual Motor
  - `assembly_plant`: e.g. Tesla Factory — Fremont, CA
  - `production_sequence`: Numeric sequence string
  - `autopilot_hardware`: e.g. HW3 or HW4

- **Additional Manual Fields**:
  - `customer`: Link to the Customer DocType for tracking ownership.
  - `license_plate`: Vehicle license plate.
  - `color`: Exterior paint color of the vehicle.
  - `manufactured_month`: Month of manufacture (e.g., 05/22), verifiable via the physical B-pillar label on the vehicle.

## Architectural Pattern

- Created with `custom=0` and `module="Induct Shop"` to ensure the schema (`repair_vehicle.json`) and client logic (`repair_vehicle.js`) are tracked in the application's source code and are available upon application reinstall.
- Adheres to the MVP constraint of servicing only Tesla vehicles by throwing validation warnings if a non-Tesla WMI is inputted.
- Fields strictly utilize standard Frappe data types (`Data`, `Check`, `Section Break`, `Column Break`) to ensure optimal filtering, reporting, and database integrity.
