---
type: Reference
title: "Getting Information From Another Document In Print Format"
description: Frappe framework development reference.
tags: [frappe, development, reference]
timestamp: 2026-06-27T07:57:07Z
---

In a print format, you can get data from another document. For example, if you have a field called `sales_order` in Sales Invoice, then you can get the sales order details using `frappe.get_doc`:


```
{% set sales_order_doc = frappe.get_doc("Sales Order", sales_order) %}

{{ sales_order_doc.customer }}
```
