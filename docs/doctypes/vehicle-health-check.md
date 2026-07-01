---
type: DocType Specification
title: Vehicle Health Check
description: Specification and feature list for the proposed Vehicle Health Check DocType.
resource: vehicle_health_check
tags: [doctype, specification, vehicle, inspection, health-check]
---

# Vehicle Health Check DocType

## Overview
The **Vehicle Health Check** DocType is a dedicated document designed to facilitate a comprehensive inspection of a vehicle, separate from the initial check-in process. It standardizes the procedure for diagnosing and recommending services, ensuring a structured approach to upselling and maintenance tracking.

## Key Features

### 1. Basic Information
- **Customer / Client:** Link to the Customer DocType to identify the owner.
- **Vehicle:** Link to the Repair Vehicle DocType to identify the specific vehicle being inspected.
- **Project:** Link to the Project DocType to associate this health check with an ongoing job.
- **Inspection Date:** Automatically logged timestamp of when the inspection occurred.

### 2. Customizable Vehicle Inspection Checklist
A dynamic and customizable checklist to document the vehicle's technical condition and identify potential issues that require attention.

- **Dynamic Checklist Items:** Use a child table to allow mechanics to customize inspection points (e.g., Exterior Condition, Dashboard Lights, Fluids, Tires, Brakes, Suspension) per inspection.
- **Service Linking:** Each inspection result item has the ability to link to a specific `Item` (Service or Part) required to address the discovered issues.
- **Condition Grading:** Ability to mark items using a traffic light system (e.g., Green/OK, Yellow/Monitor, Red/Requires Immediate Attention).

### 3. Automated Quoting
- **Quotation Generation:** A feature to automatically generate and populate a `Quotation` containing the linked services/parts for all inspection items marked as needing attention.

### 4. Media & Attachments
- **Issue Documentation:** Pictures can be directly attached to specific line items inside the inspection checklist to visually document discovered problems and provide proof to the customer.

## Data Structure / Schema Draft

| Field Label | Field Type | Description |
|---|---|---|
| Customer | Link | Link to standard Customer DocType. |
| Vehicle | Link | Link to Repair Vehicle DocType. |
| Project | Link | Link to the active Project. |
| Inspection Date | Datetime | Date and time the inspection occurred. |
| Inspection Checklist | Table | Child table for dynamic inspection items, linking to Services/Items. |
| Media | Attach | Photos of the discovered issues. |
