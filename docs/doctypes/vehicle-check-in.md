---
type: Reference
title: "Vehicle Check-in DocType"
description: "Specification and feature documentation for the Vehicle Check-in DocType, handling vehicle intake, inspection logging, automated Project creation, and Schedule Entry cross-linking."
resource: vehicle_check_in
tags: [doctype, vehicle, check-in, scheduling, reference]
status: Implemented
timestamp: 2026-08-05T14:10:00Z
---

# Vehicle Check-in DocType

## Overview
The **Vehicle Check-in** DocType is a dedicated document designed to facilitate the intake and initial inspection process when a vehicle arrives at the shop. It standardizes the check-in procedure, ensuring all necessary preliminary data is captured before any repair or project work begins.

## Key Features

### 1. Basic Intake Information
- **Customer / Client:** Link to the Customer DocType to identify the owner.
- **Vehicle:** Link to the Repair Vehicle DocType to identify the specific vehicle being checked in.
- **Schedule Entry:** Link to the originating standalone or diagnostic `Schedule Entry` (`schedule_entry`).
- **Date and Time of Intake:** Automatically logged timestamp of when the check-in occurred (`check_in_date`).
- **Intake Mileage / Odometer:** Required field (`intake_mileage`) to record the exact mileage of the vehicle at the time of drop-off. A client-side safeguard script prevents accidental modification of this field post-creation without explicit user confirmation via a dialogue.

### 2. Inspection & Damage Log
A simple table to document the vehicle's condition upon arrival. This helps protect the shop from liability and provides a baseline for the vehicle's state.

- **Inspection Template:** A template feature allowing the inspection table to be pre-populated. A `Standard` template is automatically provisioned via the `after_install` hook, containing the following required line items:
  - Manufacturing Certification Label
  - Front Left Corner
  - Front Right Corner
  - Rear Left Corner
  - Rear Right Corner
  - Interior (Front Seats)
  - Interior (Rear Seats)
  - Dashboard Mileage
  - Service Mode Alert Page
- **Damage Line Items:** The `Vehicle Check-in Item` child table allows the person inspecting the car at check-in to describe pre-existing damages. This table is auto-populated dynamically when an Inspection Template is selected.
- **Visual Documentation & Media:** Users can attach general photos or evidence directly to specific line items inside the child table to visually document pre-existing issues.

### 3. Integration & Connections
- **Automated Project Creation & Schedule Entry Cross-Linking:** Automatically creates a new Project upon saving the check-in record. The Check-in document is linked back directly to this new Project via the `after_insert` server script in the DocType controller. Generated projects use the human-readable naming scheme `"{Customer} - {Model Trim} - {Check-in ID}"` (e.g. `"John Doe - Model Y Performance - CHK-IN-2026-00001"`), ensuring unique naming across multiple check-ins for the same customer and vehicle.
- When linked to an originating `Schedule Entry` (`schedule_entry`), the `after_insert()` hook also updates the `Schedule Entry` with references to `project`, `repair_vehicle`, `customer`, and `vehicle_check_in`, seamlessly resolving quick-entry text fields to master records.


## Data Structure / Schema

| Field Label | Field Type | Description |
| --- | --- | --- |
| Customer | Link | Link to standard Customer DocType. |
| Vehicle | Link | Link to Repair Vehicle DocType (`repair_vehicle`). |
| Schedule Entry | Link | Link to originating Schedule Entry (`schedule_entry`). |
| Project | Link | Automatically generated Project for this check-in. (Read Only) |
| Intake Mileage | Int/Float | Odometer reading at check-in. |
| Check-in Date | Datetime | Date and time the vehicle arrived. |
| Inspection Template | Link | Link to Inspection Template DocType to auto-populate the table. |
| Inspection Items | Table | Child table for documenting inspections and pre-existing damages |
| Media | Attach | Photos of the vehicle condition. |

