---
type: Specification
title: "Shop Equipment Procurement Specification"
description: "Decision checklist, equipment quantities and models, EV high-voltage safety tooling, and vendor procurement tracking."
status: In Progress
tags: [business, equipment, procurement, tooling, ev-safety, shop-opening]
timestamp: 2026-08-20T17:10:00Z
---

# Shop Equipment Procurement Specification

## 1. Overview & Purpose
This document provides the decision framework, equipment inventory target checklist, vendor quote tracking, and delivery logistics for procuring all major shop machinery, diagnostic hardware, and high-voltage safety equipment for Induct Shop.

Once equipment is ordered, delivered, and commissioned on the shop floor, the active asset register, serial numbers, user manuals, warranty terms, and service contacts will be promoted to `docs/business/established/equipment-inventory.md`, and this document will be archived in `docs/business/archive/`.

---

## 2. Equipment Checklist & Quantities

Fill in model choices, quantities, and target budgets:

### 2.1 Vehicle Lifts & Bay Machinery
- [ ] 2-Post Automotive Lifts (Target Qty: `______`, Capacity: `______` lbs, Preferred Brand/Model: `______`)
- [ ] 4-Post Wheel Alignment Lift (Target Qty: `______`, Capacity: `______` lbs, Preferred Brand/Model: `______`)
- [ ] Low-Profile Scissor / EV Battery Pack Drop Lift (Target Qty: `______`, Capacity: `______` lbs, Brand: `______`)
- [ ] Heavy-Duty Hydraulic Transmission / Battery Pack Jack (Target Qty: `______`, Capacity: `______` lbs)
- [ ] Under-Hoist Support Stands (Target Qty: `______`)

### 2.2 Wheel, Tire & Alignment Systems
- [ ] Touchless / Leverless Tire Changer for EV Wheels up to 26" (Target Qty: `______`, Brand/Model: `______`)
- [ ] Dynamic Road Force Wheel Balancer (Target Qty: `______`, Brand/Model: `______`)
- [ ] 3D Optical Wheel Alignment System (Target Qty: `______`, Brand/Model: `______`)
- [ ] TPMS Sensor Programming & Diagnostic Tool (Target Qty: `______`, Brand/Model: `______`)

### 2.3 High-Voltage EV Safety Equipment & Diagnostic Tools
- [ ] Class 0 (1000V Rated) High-Voltage Insulating Gloves with Leather Protectors (Target Qty: `______` pairs)
- [ ] 1000V CAT III / CAT IV Insulated Hand Tool Sets (Sockets, Ratchets, Wrenches, Screwdrivers) (Target Qty: `______` sets)
- [ ] Milliohm / Insulation Resistance Tester (Megohmmeter for High-Voltage Isolation Checks) (Target Qty: `______`)
- [ ] High-Voltage Rescue Hook / Safety Cane (Target Qty: `______` stations)
- [ ] High-Voltage Bay Danger Stanchions & Safety Barrier Tape (Target Qty: `______` sets)
- [ ] Tesla Toolbox 3 Diagnostic Interface Hardware & PC Adapter Cables (Target Qty: `______` sets)
- [ ] Multimeter (CAT III 1000V / CAT IV 600V rated) (Target Qty: `______`)

### 2.4 Fluids, Compressed Air & Shop Floor Equipment
- [ ] Dual Refrigerant A/C Service Machine (R1234yf & R134a with POE oil separation for EVs) (Model: `______`, Qty: `______`)
- [ ] Rotary Screw / Piston Air Compressor (Motor: `______` HP, Tank: `______` Gal, CFM: `______` @ 90 PSI, Brand: `______`)
- [ ] Compressed Air Filtration, Moisture Separator & Aluminum Piping Kit (Brand: `______`)
- [ ] Coolant Vacuum Refill & Fluid Exchange Machine (Target Qty: `______`)
- [ ] Brake Fluid Pressure Bleeder (Target Qty: `______`)
- [ ] Low-Profile Heavy-Duty Shop Floor Jacks (Target Qty: `______`)

### 2.5 Total Equipment Capital Budget
- [ ] Total Target Capital Equipment Budget: `$______`
- [ ] Target Equipment Financing / Leasing Term (if applicable): `______` months (Interest / Lease rate: `______`%)

---

## 3. Site Prerequisites & Installation Checklist

- [ ] Verify concrete slab depth (`______` inches) and strength rating (`______` PSI) at lift anchor points
- [ ] Complete 3-phase and 240V dedicated electrical drops for lifts, compressor, tire machine, and A/C unit
- [ ] Complete compressed air piping layout across service bays
- [ ] Designate dedicated high-voltage battery staging / quarantine zone with fire suppression access
- [ ] Schedule professional lift installer / certification technician inspection

---

## 4. Vendor Quote Comparison Grid

Record vendor equipment packages below:

| Equipment Category | Vendor A (e.g., Rotary / Hunter) | Vendor B (e.g., BendPak / Ranger) | Vendor C (e.g., Snap-on / Matco) |
| :--- | :--- | :--- | :--- |
| **Sales Rep & Contact** | `______` | `______` | `______` |
| **Lift Package Quote** | `$______` | `$______` | `$______` |
| **Tire & Balancer Quote**| `$______` | `$______` | `$______` |
| **Alignment System** | `$______` | `$______` | `$______` |
| **A/C Machine & Fluids** | `$______` | `$______` | `$______` |
| **Air Compressor System**| `$______` | `$______` | `$______` |
| **HV Tooling & Safety** | `$______` | `$______` | `$______` |
| **Total Package Cost** | `$______` | `$______` | `$______` |
| **Delivery Lead Time** | `______` weeks | `______` weeks | `______` weeks |
| **Warranty Terms** | `______` | `______` | `______` |

---

## 5. Owner Decision Sign-Off & Promotion Trigger

- [ ] Selected Equipment Vendor(s): `______`
- [ ] Total Purchase Order / Lease Amount: `$______`
- [ ] Purchase Order executed & deposit paid: `[ ] Yes  Date: ______`
- [ ] Delivery dates confirmed: `______`
- [ ] Professional installation and safety certification completed: `[ ] Yes  Date: ______`

### Transition Trigger
When equipment is installed and commissioned:
1. Author `docs/business/established/equipment-inventory.md` containing all asset serial numbers, maintenance schedules, manufacturer warranty certificates, and technician service contacts.
2. Relocate this document to `docs/business/archive/equipment-procurement-spec.md` with `status: Archived`.
3. Update [`docs/business/index.md`](../index.md) and [`docs/log.md`](/log.md).
