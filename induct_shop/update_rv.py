import frappe

def update_repair_vehicle_doctype():
    doctype_name = "Repair Vehicle"
    
    doc = frappe.get_doc("DocType", doctype_name)
    
    new_fields = [
        {
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "license_plate",
            "label": "License Plate",
            "fieldtype": "Data"
        },
        {
            "fieldname": "color",
            "label": "Color",
            "fieldtype": "Data"
        },
        {
            "fieldname": "manufactured_month",
            "label": "Manufactured Month",
            "fieldtype": "Data",
            "description": "e.g., 05/22 (from B-pillar label)"
        }
    ]
    
    # Avoid duplicates
    existing_fields = [f.fieldname for f in doc.fields]
    
    # We will insert them right after is_valid_vin for Customer, License Plate, Color
    # And after assembly_plant for manufactured_month
    
    for f in new_fields:
        if f["fieldname"] not in existing_fields:
            doc.append("fields", f)
            
    # sort the fields manually to put them in good spots
    def get_sort_order(f):
        order = [
            "vin",
            "is_valid_vin",
            "customer",
            "license_plate",
            "color",
            "sb_details",
            "manufacturer",
            "model",
            "model_year",
            "body_type",
            "cb_drivetrain",
            "trim",
            "drivetrain",
            "battery_type",
            "drive_unit",
            "sb_production",
            "assembly_plant",
            "manufactured_month",
            "production_sequence",
            "cb_hw",
            "autopilot_hardware"
        ]
        if f.fieldname in order:
            return order.index(f.fieldname)
        return 99
        
    doc.fields.sort(key=get_sort_order)
    
    doc.save(ignore_permissions=True)
    print(f"Successfully updated '{doctype_name}' DocType.")

def execute():
    update_repair_vehicle_doctype()

