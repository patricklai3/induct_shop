import frappe

def after_install():
    create_standard_inspection_template()

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
