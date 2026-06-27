---
type: Reference
title: "Portal Roles"
description: Frappe framework development reference.
tags: [frappe, development, reference]
timestamp: 2026-06-27T07:57:07Z
---



Version: 7.1+

Roles can be assigned to Website Users and they will see menu based on their role

1. A default role can be set in **Portal Settings**
1. Each Portal Menu Item can have a role associated with it. If that role is set, then only those users having that role can see that menu item
1. Rules can be set for default roles that will be set on default users on hooks

![Portal Settings](/files/portal-settings.png)

#### Rules for Default Role

For example if the Email Address matches with a contact id, then set role Customer or Supplier:

 default_roles = [
 {'role': 'Customer', 'doctype':'Contact', 'email_field': 'email_id',
 'filters': {'ifnull(customer, "")': ('!=', '')}},
 {'role': 'Supplier', 'doctype':'Contact', 'email_field': 'email_id',
 'filters': {'ifnull(supplier, "")': ('!=', '')}},
 {'role': 'Student', 'doctype':'Student', 'email_field': 'student_email_id'}
 ]


