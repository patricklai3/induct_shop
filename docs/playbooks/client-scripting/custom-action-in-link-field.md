---
type: Reference
title: "Custom Action in Link Field"
description: Frappe framework development reference.
tags: [frappe, development, reference]
timestamp: 2026-06-27T07:57:07Z
---


You can add a new custom link option to the standard link field by defining the function in the namespace `frappe.ui.form.ControlLink.link_options`.

In the `frappe.ui.form.ControlLink.link_options`, you have access to the link field object.

### 1. Adding Custom Option

```js
frappe.ui.form.ControlLink.link_options = function(link) {
 return [
 {
 html: ""
 + " "
 + __("Custom Link Option")
 + "",
 label: __("Custom Link Option"),
 value: "custom__link_option",
 action: () => {}
 }
 ];
}
 
```

Once a function is assigned to `frappe.ui.form.ControlLink.link_options`, the link field will have a new link option:

![182354398 c1fc9f55 4464 4683 bb74 982ec2546f71](https://user-images.githubusercontent.com/7310479/182354398-c1fc9f55-4464-4683-bb74-982ec2546f71.png)
