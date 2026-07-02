import frappe

def before_uninstall():
    """
    Remove all custom fields and other customizations added by Induct Shop
    to standard Frappe/ERPNext DocTypes.
    """
    print("Removing Induct Shop customizations...")
    remove_custom_fields()
    remove_property_setters()
    remove_custom_scripts()
    print("Customizations removed successfully.")

def remove_custom_fields():
    """Remove all custom fields added by Induct Shop."""
    # 1. Remove fields correctly tagged with our module
    custom_fields = frappe.get_all("Custom Field", filters={"module": "Induct Shop"})
    for field in custom_fields:
        frappe.delete_doc("Custom Field", field.name, ignore_missing=True)
        
    # 2. Remove specific fields that might lack the module tag (fallback/explicit)
    explicit_fields = [
        'Quotation-repair_vehicle', 
        'Sales Order-repair_vehicle', 
        'Sales Invoice-repair_vehicle'
    ]
    for cf in explicit_fields:
        if frappe.db.exists('Custom Field', cf):
            frappe.delete_doc('Custom Field', cf, ignore_missing=True)

def remove_property_setters():
    """Remove all property setters added by Induct Shop."""
    property_setters = frappe.get_all("Property Setter", filters={"module": "Induct Shop"})
    for setter in property_setters:
        frappe.delete_doc("Property Setter", setter.name, ignore_missing=True)

def remove_custom_scripts():
    """Remove all client scripts and server scripts added by Induct Shop."""
    if frappe.db.exists("DocType", "Client Script"):
        client_scripts = frappe.get_all("Client Script", filters={"module": "Induct Shop"})
        for script in client_scripts:
            frappe.delete_doc("Client Script", script.name, ignore_missing=True)
            
    if frappe.db.exists("DocType", "Server Script"):
        server_scripts = frappe.get_all("Server Script", filters={"module": "Induct Shop"})
        for script in server_scripts:
            frappe.delete_doc("Server Script", script.name, ignore_missing=True)
