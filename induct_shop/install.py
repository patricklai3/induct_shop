import frappe

def after_install():
    create_standard_inspection_template()
    enable_batch_wise_valuation()
    seed_equipment_tags()
    seed_item_attributes()
    seed_schedule_entry_types()

def after_migrate():
    seed_schedule_entry_types()

STANDARD_SCHEDULE_ENTRY_TYPES = [
    {
        "type_name": "Diagnostic",
        "requires_sales_order": 0,
        "color": "#1f538d",
        "description": "Initial inspection and diagnostic slot"
    },
    {
        "type_name": "Repair",
        "requires_sales_order": 1,
        "color": "#2e7d32",
        "description": "Confirmed repair job"
    },
    {
        "type_name": "Meeting",
        "requires_sales_order": 0,
        "color": "#7b1fa2",
        "description": "Internal staff or shop meeting"
    },
    {
        "type_name": "Maintenance / Shop Cleaning",
        "requires_sales_order": 0,
        "color": "#c62828",
        "description": "Service bay or equipment maintenance"
    },
    {
        "type_name": "Internal Service",
        "requires_sales_order": 0,
        "color": "#ef6c00",
        "description": "Internal vehicle maintenance or fleet service"
    }
]

def seed_schedule_entry_types():
    if not frappe.db.exists("DocType", "Schedule Entry Type"):
        return
    for item in STANDARD_SCHEDULE_ENTRY_TYPES:
        if not frappe.db.exists("Schedule Entry Type", item["type_name"]):
            doc = frappe.get_doc({
                "doctype": "Schedule Entry Type",
                "type_name": item["type_name"],
                "requires_sales_order": item["requires_sales_order"],
                "color": item["color"],
                "description": item["description"]
            })
            doc.insert(ignore_permissions=True)


def seed_equipment_tags():
    if frappe.db.exists("DocType", "Equipment Tag") and not frappe.db.exists("Equipment Tag", "Lift"):
        doc = frappe.get_doc({
            "doctype": "Equipment Tag",
            "tag_name": "Lift",
            "description": "Standard automotive lift"
        })
        doc.insert(ignore_permissions=True)

def seed_item_attributes():
    from induct_shop.api.service_parts_selector import _ensure_item_attribute
    _ensure_item_attribute("Revision")
    _ensure_item_attribute("Condition", ["New", "Used", "Reconditioned"])
    _ensure_item_attribute("OEM Status", ["OEM", "Aftermarket"])

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
