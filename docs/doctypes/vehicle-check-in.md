---
type: DocType Specification
title: Vehicle Check-in
description: Specification and feature list for the proposed Vehicle Check-in DocType.
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
- **Date and Time of Intake:** Automatically logged timestamp of when the check-in occurred.
- **Intake Mileage / Odometer:** Required field to record the exact mileage of the vehicle at the time of drop-off.

### 2. Inspection & Damage Log
A simple table to document the vehicle's condition upon arrival. This helps protect the shop from liability and provides a baseline for the vehicle's state.

- **Inspection Template:** A template feature, similar to tax templates, allowing the inspection table to be pre-populated. The app will come preloaded with a standard template containing the following required line items:
  - Manufacturing Certification Label
  - Front Left Corner
  - Front Right Corner
  - Rear Left Corner
  - Rear Right Corner
  - Interior (Front Seats)
  - Interior (Rear Seats)
  - Dashboard Mileage
  - Service Mode Alert Page
- **Damage Line Items:** A child table to allow the person inspecting the car at check-in to describe pre-existing damages (e.g., dents, scratches, interior tears) the customer has on their car. This table can be populated via the Inspection Template.
- **Visual Documentation & Media:** Ability to upload general photos of the vehicle (all four corners, interior, dashboard mileage/lights) at the time of drop-off. Pictures can also be directly attached to specific line items inside the damage log to visually document the pre-existing issues.

### 3. Integration & Connections
- **Automated Project Creation:** Automatically create a new Project upon saving the check-in record, as the vehicle has arrived at the shop. The Check-in document should be directly linked to this new Project.

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

