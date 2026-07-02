---
type: DocType Specification
title: Vehicle Check-in
description: Specification and feature list for the implemented Vehicle Check-in DocType.
resource: vehicle_check_in
tags: [doctype, specification, vehicle, check-in]
---

# Vehicle Check-in DocType

## Overview
The **Vehicle Check-in** DocType is a dedicated document designed to facilitate the intake and initial inspection process when a vehicle arrives at the shop. It standardizes the check-in procedure, ensuring all necessary preliminary data is captured before any repair or project work begins.

## Key Features

### 1. Basic Intake Information
- **Customer / Client:** Link to the Customer DocType to identify the owner.
- **Vehicle:** Link to the Repair Vehicle DocType to identify the specific vehicle being checked in.
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
- **Automated Project Creation:** Automatically creates a new Project upon saving the check-in record. The Check-in document is linked back directly to this new Project via the `after_insert` server script in the DocType controller.

## Data Structure / Schema Draft

| Field Label | Field Type | Description |
|---|---|---|
| Customer | Link | Link to standard Customer DocType. |
| Vehicle | Link | Link to Repair Vehicle DocType. |
| Project | Link | Automatically generated Project for this check-in. (Read Only) |
| Intake Mileage | Int/Float | Odometer reading at check-in. |
| Check-in Date | Datetime | Date and time the vehicle arrived. |
| Inspection Template | Link | Link to Inspection Template DocType to auto-populate the table. |
| Inspection Items | Table | Child table for documenting inspections and pre-existing damages |
| Media | Attach | Photos of the vehicle condition. |

