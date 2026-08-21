---
type: Specification
title: "IT Infrastructure & Telephony Setup Specification"
description: "Decision checklist, hardware parameters, Telnyx VoIP/SMS routing, and technician digital intake tooling."
status: In Progress
tags: [business, it, telephony, networking, telnyx, hardware, shop-opening]
timestamp: 2026-08-20T17:10:00Z
---

# IT Infrastructure & Telephony Setup Specification

## 1. Overview & Purpose
This document provides the technical requirements, equipment checklists, telephony routing configurations, and vendor comparison framework for provisioning Induct Shop's IT network, hardware, and customer communication pipeline.

Once the network and communication systems are deployed and operational, the active network topology, IP address schema, Telnyx SIP configurations, hardware inventory, and vendor support contracts will be promoted to `docs/business/established/it-and-telephony.md`, and this document will be archived in `docs/business/archive/`.

---

## 2. IT Infrastructure Parameters & Hardware Checklist

Fill in quantities, model choices, and network parameters:

### 2.1 Internet Service & Networking
- [ ] Primary Internet Service Provider (ISP): `______` (Speed: `______` Mbps Down / `______` Mbps Up, Monthly Cost: `$______`)
- [ ] Backup Failover ISP / 5G Cellular Modem: `______` (Monthly Cost: `$______`)
- [ ] Commercial Router / Firewall Gateway: `______`
- [ ] Managed PoE Network Switch (`______` Ports, Model: `______`)
- [ ] Wi-Fi 6 Access Points covering shop floor, bays, and customer lounge (Qty: `______`, Model: `______`)
- [ ] Dedicated Guest Wi-Fi VLAN and Isolated Point-of-Sale / Internal VLAN: `[ ] Configured`

### 2.2 Telephony & Automated Messaging (Telnyx / VoIP)
- [ ] Primary Business Telephone Number: `______`
- [ ] Secondary / Dedicated SMS Number: `______`
- [ ] Inbound Call Routing Flow (Auto-Attendant / Ring Group / Voicemail): `______`
- [ ] Desk VoIP Handsets for Reception & Office (Qty: `______`, Model: `______`)
- [ ] Cordless DECT Handsets for Shop Floor (Qty: `______`, Model: `______`)
- [ ] Telnyx 10DLC A2P Brand and Campaign Registration for Automated Customer SMS: `[ ] Submitted`
- [ ] Induct Shop Frappe webhook integration with Telnyx for automated status alerts: `[ ] Configured`

### 2.3 Shop Floor & Office Computing Hardware
- [ ] Front Desk Reception Workstations (Qty: `______`, Specs: `______`)
- [ ] Ruggedized Technician Tablets for Vehicle Check-in & Digital Inspections (Qty: `______`, Model: `______`)
- [ ] Protective Tablet Cases & Handstraps / Wall Docking Stations (Qty: `______`)
- [ ] Handheld 2D Bluetooth Barcode & VIN Scanners (Qty: `______`, Model: `______`)
- [ ] Thermal Label Printer for Vehicle Key Tags & Parts Binning (Qty: `______`, Model: `______`)
- [ ] Laser Multi-Function Document / Customer Invoice Printer (Qty: `______`, Model: `______`)
- [ ] Uninterruptible Power Supplies (UPS Battery Backups) (Qty: `______`)

### 2.4 Software Subscriptions & Monthly IT Budget
- [ ] Monthly Internet & Backup ISP Budget: `$______` / mo
- [ ] Monthly Telephony / Telnyx SIP & Messaging Budget: `$______` / mo
- [ ] Software Subscriptions (ERP Hosting, Tesla Toolbox, Google Workspace): `$______` / mo
- [ ] Hardware Acquisition Capital Budget: `$______`

---

## 3. Deployment & Verification Tasks

- [ ] Run Ethernet drops to front desk, service bay kiosks, access points, and office printer
- [ ] Verify seamless Wi-Fi coverage with -65 dBm or better signal strength across all vehicle lifts
- [ ] Configure firewall rules and isolate customer guest Wi-Fi from internal Frappe/ERP network
- [ ] Test end-to-end inbound customer call routing and after-hours voicemail delivery to email
- [ ] Test automated SMS sending via Telnyx API for vehicle check-in confirmation and quote approvals
- [ ] Enroll technician tablets in Mobile Device Management (MDM) with kiosk mode for Induct Shop Desk

---

## 4. Vendor Quote Comparison Grid

Record candidate hardware and IT service proposals below:

| Component / Service | Vendor / Option A | Vendor / Option B | Vendor / Option C |
| :--- | :--- | :--- | :--- |
| **Networking Hardware (UniFi / Cisco / TP-Link)** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Technician Tablets (iPad / Galaxy Active / Surface)**| `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Workstations & Monitors** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **VoIP Handsets (Yealink / Poly)** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Barcode Scanners & Label Printers** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Total Hardware Cost** | `$______` | `$______` | `$______` |
| **Delivery Lead Time** | `______` days | `______` days | `______` days |

---

## 5. Owner Decision Sign-Off & Promotion Trigger

- [ ] Selected Hardware Vendor(s): `______`
- [ ] Selected ISP Provider: `______`
- [ ] Total Hardware Capital Expenditure: `$______`
- [ ] Hardware purchased & delivered: `[ ] Yes  Date: ______`
- [ ] Network configured & Telnyx telephony activated: `[ ] Yes  Date: ______`

### Transition Trigger
When the IT network, hardware, and telephony are fully operational:
1. Author `docs/business/established/it-and-telephony.md` containing active network topology diagrams, router admin credentials location, Telnyx account IDs, hardware asset list with serial numbers, and IT support contacts.
2. Relocate this document to `docs/business/archive/it-and-telephony-setup-spec.md` with `status: Archived`.
3. Update [`docs/business/index.md`](../index.md) and [`docs/log.md`](/log.md).
