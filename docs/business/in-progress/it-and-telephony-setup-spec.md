---
type: Specification
title: "IT Infrastructure & Telephony Setup Specification"
description: "Decision checklist, Canadian ISP redundancy, Telnyx VoIP/SMS routing, and technician digital intake tooling."
status: In Progress
tags: [business, it, telephony, networking, telnyx, hardware, ontario, shop-opening]
timestamp: 2026-08-21T00:00:00Z
---

# IT Infrastructure & Telephony Setup Specification

## 1. Overview & Purpose

This document provides the technical requirements, equipment checklists, telephony routing configurations, and vendor comparison framework for provisioning Induct Shop's IT network, hardware, and customer communication pipeline in **Kitchener-Waterloo, Ontario**.

Once the network and communication systems are deployed and operational, the active network topology, IP address schema, Telnyx SIP configurations, hardware inventory, and vendor support contracts will be promoted to `docs/business/established/it-and-telephony.md`, and this document will be archived in `docs/business/archive/`.

---

## 2. IT Infrastructure Parameters & Hardware Checklist

Fill in quantities, model choices, and network parameters for owner review:

### 2.1 Internet Service & Networking (Kitchener-Waterloo)
- [ ] Primary Internet Service Provider (ISP): `______` (e.g., Bell Business Fibe / Rogers Business) (Speed: `______` Mbps Down / `______` Mbps Up, Monthly Cost: `$______` CAD)
- [ ] Backup Failover ISP / 5G Cellular Gateway: `______` (Monthly Cost: `$______` CAD)
- [ ] Commercial Router / Firewall Gateway: `______`
- [ ] Managed PoE Network Switch (`______` Ports, Model: `______`)
- [ ] Wi-Fi 6 Access Points covering shop floor, mechanical bays, and customer lounge (Qty: `______`, Model: `______`)
- [ ] Dedicated Guest Wi-Fi VLAN isolated from internal Frappe/ERP and point-of-sale network: `[ ] Configured`

### 2.2 Telephony & Automated Messaging (Telnyx / Canadian Telecom)
- [ ] Primary Local Business Telephone Number (Area Code 519 / 226 / 548): `______`
- [ ] Dedicated Automated SMS Number: `______`
- [ ] Inbound Call Routing Flow (Auto-Attendant / Ring Group / Voicemail): `______`
- [ ] Desk VoIP Handsets for Reception & Office (Qty: `______`, Model: `______`)
- [ ] Cordless Rugged DECT Handsets for Shop Floor (Qty: `______`, Model: `______`)
- [ ] Canadian A2P 10DLC Campaign & Brand Registration submitted: `[ ] Submitted`
- [ ] Canadian Anti-Spam Legislation (CASL) consent and opt-out workflows verified for customer SMS/email: `[ ] Verified`
- [ ] Induct Shop Frappe webhook integration with Telnyx for automated status alerts: `[ ] Configured`

### 2.3 Shop Floor & Office Computing Hardware
- [ ] Front Desk Reception Workstations / Monitors (Qty: `______`, Specs: `______`)
- [ ] Ruggedized Technician Tablets for Vehicle Check-in & Digital Inspections (Qty: `______`, Model: `______`)
- [ ] Protective Tablet Cases, Handstraps & Magnetic Wall Docks (Qty: `______`)
- [ ] Handheld 2D Bluetooth Barcode & VIN Scanners (Qty: `______`, Model: `______`)
- [ ] Thermal Label Printer for Vehicle Key Tags & Parts Binning (Qty: `______`, Model: `______`)
- [ ] Multi-Function Customer Invoice & Document Printer (Qty: `______`, Model: `______`)
- [ ] Uninterruptible Power Supplies (UPS Battery Backups) (Qty: `______`)

### 2.4 Monthly Subscriptions & Capital IT Budget
- [ ] Monthly Internet & Backup ISP Budget: `$______` CAD / mo
- [ ] Monthly Telephony / Telnyx SIP & Messaging Budget: `$______` CAD / mo
- [ ] Software Subscriptions (Google Workspace, Tesla Toolbox, Cloud Hosting): `$______` CAD / mo
- [ ] Hardware Acquisition Capital Budget: `$______` CAD

---

## 3. Deployment & Verification Tasks

- [ ] Run Ethernet drops to reception desk, mechanical bay workstations, access points, and office printer
- [ ] Verify seamless Wi-Fi coverage with -65 dBm or better signal strength across all vehicle lifts
- [ ] Configure firewall rules and isolate customer guest Wi-Fi from internal Frappe/ERP network
- [ ] Test end-to-end inbound customer call routing and after-hours voicemail delivery to email
- [ ] Test automated SMS sending via Telnyx API for vehicle check-in confirmation and quote approvals
- [ ] Enroll technician tablets in Mobile Device Management (MDM) with kiosk mode for Induct Shop Desk

---

## 4. Hardware & IT Vendor Quote Comparison Grid

Record candidate hardware and IT service proposals below:

| Component / Service | Vendor / Option A | Vendor / Option B | Vendor / Option C |
| :--- | :--- | :--- | :--- |
| **Networking Hardware (UniFi / Cisco / TP-Link)** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Technician Tablets (iPad / Galaxy Active / Surface)**| `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Workstations & Monitors** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **VoIP Handsets (Yealink / Poly)** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Barcode Scanners & Label Printers** | `______` ($`______`) | `______` ($`______`) | `______` ($`______`) |
| **Total Hardware Cost (CAD)** | `$______` | `$______` | `$______` |
| **Delivery Lead Time** | `______` days | `______` days | `______` days |

---

## 5. Owner Decision Sign-Off & Promotion Trigger

- [ ] Selected Hardware Vendor(s): `______`
- [ ] Selected Primary ISP Provider: `______`
- [ ] Total Hardware Capital Expenditure: `$______` CAD
- [ ] Hardware purchased & delivered: `[ ] Yes  Date: ______`
- [ ] Network configured & Telnyx telephony activated: `[ ] Yes  Date: ______`

### Transition Trigger
When the IT network, hardware, and telephony are fully operational:
1. Author `docs/business/established/it-and-telephony.md` containing active network topology diagrams, router admin credentials location, Telnyx account IDs, hardware asset list with serial numbers, and IT support contacts.
2. Relocate this document to `docs/business/archive/it-and-telephony-setup-spec.md` with `status: Archived`.
3. Update [`docs/business/index.md`](../index.md) and [`docs/log.md`](/log.md).
