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

### 2. Customizable Vehicle Inspection Checklist
A customizable checklist (via a separate template or child table) to document the vehicle's condition upon arrival. This helps protect the shop from liability and provides a baseline for the vehicle's state.

- **Dynamic Checklist Items:** Instead of static fields, use a child table to allow mechanics to customize inspection points (e.g., Exterior Condition, Dashboard Lights, Fluids, Tires) per check-in.
- **Service Linking:** Each inspection result item has the ability to link to a specific `Item` (Service or Part) required to address the discovered issues.
- **Automated Quoting:** A feature to automatically generate and populate a `Quotation` containing the linked services/parts for all inspection items marked as needing attention.

### 3. Intake Media & Attachments
- **General Photos:** Ability to upload general photos of the vehicle (all four corners, interior, dashboard mileage/lights) at the time of drop-off.
- **Issue Documentation:** Pictures can be directly attached to specific line items inside the inspection checklist to visually document discovered problems.

### 4. Integration & Connections
- **Project / Work Order Link:** Ability to create or link to a Project or subsequent Work Order directly from the Check-in document.
- **Quotation Link:** Direct connection to the automatically generated Quotation for discovered issues.
- **Customer Signature:** (Optional) Digital signature field for the customer to acknowledge the check-in condition and mileage.

## Data Structure / Schema Draft

| Field Label | Field Type | Description |
|---|---|---|
| Customer | Link | Link to standard Customer DocType. |
| Vehicle | Link | Link to Repair Vehicle DocType. |
| Intake Mileage | Int/Float | Odometer reading at check-in. |
| Check-in Date | Datetime | Date and time the vehicle arrived. |
| Inspection Checklist | Table | Child table for dynamic inspection items, linking to Services/Items. |
| Media | Attach | Photos of the vehicle condition. |

