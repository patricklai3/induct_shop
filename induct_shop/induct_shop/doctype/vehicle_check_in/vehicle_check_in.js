// Copyright (c) 2026, Induct and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Check-in", {
    refresh(frm) {
        // Store original odometer on load to revert if user cancels
        if (!frm.is_new()) {
            frm._original_mileage = frm.doc.intake_mileage;
        }
    },
    
    intake_mileage(frm) {
        if (!frm.is_new() && frm.doc.intake_mileage != frm._original_mileage) {
            frappe.confirm(
                __("Are you sure the original odometer entry was incorrect? If not, please cancel to revert to the previous value."),
                () => {
                    // User confirmed, update the stored original to avoid repeated prompts
                    frm._original_mileage = frm.doc.intake_mileage;
                },
                () => {
                    // User cancelled, revert to original
                    frm.set_value("intake_mileage", frm._original_mileage);
                }
            );
        }
    },

    inspection_template(frm) {
        if (frm.doc.inspection_template) {
            frappe.db.get_doc("Inspection Template", frm.doc.inspection_template)
                .then(doc => {
                    if (doc && doc.items) {
                        // Clear existing table to avoid duplicates? Or just append?
                        // Usually template selection clears and populates, or appends. Let's clear for safety if they switch templates.
                        frm.clear_table("inspection_items");
                        
                        doc.items.forEach(item => {
                            let child = frm.add_child("inspection_items");
                            child.inspection_description = item.inspection_description;
                        });
                        
                        frm.refresh_field("inspection_items");
                    }
                });
        }
    }
});
