import frappe

def create_repair_vehicle_doctype():
    doctype_name = "Repair Vehicle"
    
    if frappe.db.exists("DocType", doctype_name):
        print(f"DocType '{doctype_name}' already exists.")
        return
        
    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype_name,
        "module": "Induct Shop",
        "custom": 0,
        "istable": 0,
        "naming_rule": "Expression",
        "autoname": "format:{vin}",
        "fields": [
            {
                "fieldname": "vin",
                "label": "VIN",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
                "bold": 1
            },
            {
                "fieldname": "is_valid_vin",
                "label": "Is Valid VIN?",
                "fieldtype": "Check",
                "read_only": 1
            },
            {
                "fieldname": "sb_details",
                "label": "Vehicle Details",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "manufacturer",
                "label": "Manufacturer",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "model",
                "label": "Model",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "model_year",
                "label": "Model Year",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "body_type",
                "label": "Body Type",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "cb_drivetrain",
                "label": "Drivetrain Specs",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "trim",
                "label": "Trim",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "drivetrain",
                "label": "Drivetrain",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "battery_type",
                "label": "Battery Type",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "drive_unit",
                "label": "Drive Unit",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "sb_production",
                "label": "Production & Hardware",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "assembly_plant",
                "label": "Assembly Plant",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "production_sequence",
                "label": "Production Sequence",
                "fieldtype": "Data",
                "read_only": 1
            },
            {
                "fieldname": "cb_hw",
                "label": "Hardware",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "autopilot_hardware",
                "label": "Autopilot Hardware",
                "fieldtype": "Data",
                "read_only": 1
            }
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "submit": 0,
                "cancel": 0,
                "amend": 0
            }
        ],
        "show_name_in_global_search": 1,
        "track_changes": 1
    })
    
    doc.insert(ignore_permissions=True)
    print(f"Successfully created '{doctype_name}' DocType.")

def execute():
    create_repair_vehicle_doctype()

