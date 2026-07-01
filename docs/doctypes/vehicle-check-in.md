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

### 2. Pre-existing Damage Log
A simple table to document the vehicle's condition upon arrival. This helps protect the shop from liability and provides a baseline for the vehicle's state.

- **Damage Line Items:** A child table to allow the person inspecting the car at check-in to describe pre-existing damages (e.g., dents, scratches, interior tears) the customer has on their car.
- **Visual Documentation:** Pictures can be directly attached to specific line items inside the damage log to visually document the pre-existing issues.

### 3. Intake Media & Attachments
- **General Photos:** Ability to upload general photos of the vehicle (all four corners, interior, dashboard mileage/lights) at the time of drop-off.
- **Damage Photos:** As mentioned above, pictures can be attached to the specific pre-existing damage line items.

### 4. Integration & Connections
- **Automated Project Creation:** Automatically create a new Project upon saving the check-in record, as the vehicle has arrived at the shop. The Check-in document should be directly linked to this new Project.
- **Customer Signature:** (Optional) Digital signature field for the customer to acknowledge the check-in condition and mileage.

## Data Structure / Schema Draft

| Field Label | Field Type | Description |
|---|---|---|
| Customer | Link | Link to standard Customer DocType. |
| Vehicle | Link | Link to Repair Vehicle DocType. |
| Project | Link | Automatically generated Project for this check-in. (Read Only) |
| Intake Mileage | Int/Float | Odometer reading at check-in. |
| Check-in Date | Datetime | Date and time the vehicle arrived. |
| Pre-existing Damages | Table | Child table for documenting existing damages on the vehicle. |
| Media | Attach | Photos of the vehicle condition. |

