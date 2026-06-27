import frappe

def execute():
    doc = frappe.get_doc("DocType", "Repair Vehicle")
    
    order = [
        "customer",
        "license_plate",
        "color",
        "vin",
        "is_valid_vin",
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
        "production_sequence",
        "cb_hw",
        "autopilot_hardware",
        "manufactured_month"
    ]
    
    # Sort fields based on the order list
    doc.fields.sort(key=lambda f: order.index(f.fieldname) if f.fieldname in order else 99)
    
    # Reassign idx
    for i, f in enumerate(doc.fields):
        f.idx = i + 1
        
    doc.save(ignore_permissions=True)
    print("Successfully reordered fields and reassigned idx.")
