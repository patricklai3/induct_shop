---
type: Specification
title: "Commercial Insurance Selection Specification"
description: "Decision checklist, coverage limit parameters, EV risk riders, and broker quote evaluations for shop insurance."
status: In Progress
tags: [business, insurance, risk-management, liability, shop-opening]
timestamp: 2026-08-20T17:10:00Z
---

# Commercial Insurance Selection Specification

## 1. Overview & Purpose
This document establishes the risk management requirements, coverage parameter targets, and broker quote evaluation framework for securing Induct Shop's commercial insurance portfolio.

Once the insurance provider and policy packages are finalized and bound, the active policy numbers, coverage schedules, broker contacts, and claims filing procedures will be promoted to `docs/business/established/commercial-insurance.md`, and this document will be archived in `docs/business/archive/`.

---

## 2. Target Coverage Parameters & Limits Checklist

Fill in the target limits and check off parameters as decisions are confirmed:

### 2.1 Commercial General Liability (CGL)
- [ ] General Liability per occurrence limit: `$______`
- [ ] General Liability general aggregate limit: `$______`
- [ ] Products & Completed Operations aggregate limit: `$______`
- [ ] Damage to Rented Premises (Fire Legal Liability): `$______`
- [ ] Medical Expense limit (any one person): `$______`

### 2.2 Garagekeepers Liability (Customer Vehicle Protection)
- [ ] Garagekeepers total lot / location limit: `$______`
- [ ] Garagekeepers maximum per-vehicle limit: `$______`
- [ ] Selected coverage type (Direct Primary / Legal Liability): `______`
  *(Note: Direct Primary is recommended for high-value customer electric vehicles).*
- [ ] Comprehensive deductible per vehicle: `$______` (Maximum lot aggregate: `$______`)
- [ ] Collision deductible per vehicle: `$______`

### 2.3 Property, Tools & Business Interruption
- [ ] Business Personal Property (Shop equipment, diagnostic tools, inventory) limit: `$______`
- [ ] Tenant Improvements and Betterments (TIB) coverage: `$______`
- [ ] Technicians' Employee Tools & Equipment floaters: `$______`
- [ ] Inland Marine / Mobile Tool & In-Transit Parts coverage: `$______`
- [ ] Business Income & Extra Expense (Interruption) coverage: `$______` / `______` months

### 2.4 Specialized EV & High-Voltage Riders
- [ ] Confirm coverage for high-voltage battery storage, thermal runaway events, and hazmat cleanup
- [ ] Confirm technician test-driving and mobile field service / roadside triage coverage
- [ ] Cyber Liability & Customer Data Breach coverage limit: `$______`
- [ ] Employment Practices Liability Insurance (EPLI) limit: `$______`

### 2.5 Workers' Compensation & Umbrella
- [ ] Workers' Compensation Statutory Limits (Part A): `[ ] Included`
- [ ] Employer's Liability (Part B) - Bodily Injury by Accident limit: `$______`
- [ ] Employer's Liability (Part B) - Bodily Injury by Disease policy limit: `$______`
- [ ] Commercial Umbrella / Excess Liability total limit: `$______`
- [ ] Maximum target annual insurance budget across all lines: `$______` / year

---

## 3. Broker & Carrier Quote Comparison Matrix

Record candidate insurance proposals below:

| Parameter | Broker / Carrier A | Broker / Carrier B | Broker / Carrier C |
| :--- | :--- | :--- | :--- |
| **Brokerage / Agency** | `______` | `______` | `______` |
| **Underwriting Carrier(s)** | `______` | `______` | `______` |
| **Broker Contact & Phone** | `______` | `______` | `______` |
| **General Liability Limit** | `$______ / $______` | `$______ / $______` | `$______ / $______` |
| **Garagekeepers Limit** | `$______` (Direct Primary: `[ ] Yes [ ] No`) | `$______` (Direct Primary: `[ ] Yes [ ] No`) | `$______` (Direct Primary: `[ ] Yes [ ] No`) |
| **Property / Equipment Limit**| `$______` | `$______` | `$______` |
| **Workers' Comp Premium** | `$______` / yr | `$______` / yr | `$______` / yr |
| **Umbrella Limit** | `$______` | `$______` | `$______` |
| **High-Voltage EV Rider?** | `[ ] Included  [ ] Excluded` | `[ ] Included  [ ] Excluded` | `[ ] Included  [ ] Excluded` |
| **Total Annual Premium** | `$______` / yr | `$______` / yr | `$______` / yr |
| **Deductibles** | `$______` | `$______` | `$______` |
| **Key Exclusions / Limitations** | `______` | `______` | `______` |

---

## 4. Owner Decision Sign-Off & Promotion Trigger

- [ ] Selected Broker / Agency: `______`
- [ ] Selected Underwriting Carrier(s): `______`
- [ ] Final Bound Annual Premium: `$______` / yr
- [ ] Policy effective start date: `______`
- [ ] Down payment made & Certificates of Insurance (COI) received: `[ ] Yes  Date: ______`
- [ ] Landlord added as Additional Insured on General Liability: `[ ] Yes`

### Transition Trigger
When coverage is bound:
1. Author `docs/business/established/commercial-insurance.md` containing all policy numbers, coverage summary schedules, broker phone/email, Certificate of Insurance (COI) retrieval steps, and claims submission workflow.
2. Relocate this document to `docs/business/archive/insurance-selection-spec.md` with `status: Archived`.
3. Update [`docs/business/index.md`](../index.md) and [`docs/log.md`](/log.md).
