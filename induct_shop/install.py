import frappe

def after_install():
    create_standard_inspection_template()
    enable_batch_wise_valuation()

def enable_batch_wise_valuation():
    if frappe.db.exists("DocType", "Stock Settings"):
        frappe.db.set_value("Stock Settings", None, "enable_serial_and_batch_no_for_item", 1)
        frappe.db.set_value("Stock Settings", None, "do_not_use_batchwise_valuation", 0)

def create_standard_inspection_template():
    if not frappe.db.exists("Inspection Template", "Standard"):
        doc = frappe.get_doc({
            "doctype": "Inspection Template",
            "template_name": "Standard",
            "items": [
                {"inspection_description": "Manufacturing Certification Label"},
                {"inspection_description": "Front Left Corner"},
                {"inspection_description": "Front Right Corner"},
                {"inspection_description": "Rear Left Corner"},
                {"inspection_description": "Rear Right Corner"},
                {"inspection_description": "Interior (Front Seats)"},
                {"inspection_description": "Interior (Rear Seats)"},
                {"inspection_description": "Dashboard Mileage"},
                {"inspection_description": "Service Mode Alert Page"}
            ]
        })
        doc.insert(ignore_permissions=True)
