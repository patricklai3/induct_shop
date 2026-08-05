import frappe
from induct_shop.install import seed_schedule_entry_types

PREFIX = "_IST_"

EQUIPMENT_TAGS = ["Lift", "Alignment Rack", "HV Battery Station"]

SERVICE_BAYS = {
    f"{PREFIX}Bay 1": {
        "is_active": 1,
        "description": "Primary service bay",
        "equipment": [{"equipment_tag": "Lift"}]
    },
    f"{PREFIX}Bay 2": {
        "is_active": 1,
        "description": "Alignment bay",
        "equipment": [{"equipment_tag": "Lift"}, {"equipment_tag": "Alignment Rack"}]
    },
    f"{PREFIX}Bay 3": {
        "is_active": 0,
        "description": "Inactive bay",
        "equipment": []
    }
}

CUSTOMER = f"{PREFIX}Customer"

EMPLOYEES = {
    "tech_active_1": {
        "first_name": f"{PREFIX}Tech",
        "last_name": "One",
        "employee_name": f"{PREFIX}Tech One",
        "status": "Active",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "date_of_joining": "2020-01-01"
    },
    "tech_active_2": {
        "first_name": f"{PREFIX}Tech",
        "last_name": "Two",
        "employee_name": f"{PREFIX}Tech Two",
        "status": "Active",
        "gender": "Female",
        "date_of_birth": "1992-02-02",
        "date_of_joining": "2021-01-01"
    },
    "tech_inactive": {
        "first_name": f"{PREFIX}Tech",
        "last_name": "Three",
        "employee_name": f"{PREFIX}Tech Three",
        "status": "Left",
        "gender": "Male",
        "date_of_birth": "1988-03-03",
        "date_of_joining": "2019-01-01",
        "relieving_date": "2022-01-01"
    }
}

ITEMS = {
    f"{PREFIX}SERVICE_001": {
        "item_code": f"{PREFIX}SERVICE_001",
        "item_name": "Test Service 001",
        "description": "Test brake service description",
        "item_group": "Services",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "stock_uom": "Hour",
        "custom_frt": 1.5
    },
    f"{PREFIX}EST_ITEM_001": {
        "item_code": f"{PREFIX}EST_ITEM_001",
        "item_name": "Test Brake Pad Front",
        "item_group": "Brake",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "stock_uom": "Hour",
        "custom_frt": 1.0
    },
    f"{PREFIX}EST_ITEM_002": {
        "item_code": f"{PREFIX}EST_ITEM_002",
        "item_name": "Test Brake Rotor Rear",
        "item_group": "Brake",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "stock_uom": "Hour",
        "custom_frt": 1.5
    }
}

def setup_all():
    """Idempotently seeds all standard test master records."""
    ensure_uom()
    ensure_item_groups()
    ensure_equipment_tags()
    ensure_service_bays()
    ensure_customer()
    ensure_designation()
    emp_map = ensure_employees()
    ensure_items()
    ensure_shop_settings()
    seed_schedule_entry_types()
    frappe.db.commit()
    return emp_map


def ensure_uom():
    if not frappe.db.exists("UOM", "Hour"):
        frappe.get_doc({"doctype": "UOM", "uom_name": "Hour"}).insert(ignore_permissions=True)

def ensure_item_groups():
    for group in ["Services", "Brake"]:
        if not frappe.db.exists("Item Group", group):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group,
                "parent_item_group": "All Item Groups"
            }).insert(ignore_permissions=True)

def ensure_equipment_tags():
    for tag in EQUIPMENT_TAGS:
        if not frappe.db.exists("Equipment Tag", tag):
            frappe.get_doc({
                "doctype": "Equipment Tag",
                "tag_name": tag,
                "description": f"Test tag {tag}"
            }).insert(ignore_permissions=True)

def ensure_service_bays():
    for bay_name, data in SERVICE_BAYS.items():
        if not frappe.db.exists("Service Bay", bay_name):
            doc = frappe.get_doc({
                "doctype": "Service Bay",
                "bay_name": bay_name,
                "is_active": data["is_active"],
                "description": data["description"],
                "equipment": data["equipment"]
            })
            doc.insert(ignore_permissions=True)
        else:
            curr_val = frappe.db.get_value("Service Bay", bay_name, "is_active")
            if curr_val != data["is_active"]:
                frappe.db.set_value("Service Bay", bay_name, "is_active", data["is_active"])

def ensure_customer():
    if not frappe.db.exists("Customer", CUSTOMER):
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": CUSTOMER,
            "customer_group": "Commercial",
            "territory": "All Territories"
        }).insert(ignore_permissions=True)

def ensure_designation():
    if not frappe.db.exists("Designation", "Technician"):
        frappe.get_doc({
            "doctype": "Designation",
            "designation_name": "Technician"
        }).insert(ignore_permissions=True)

def ensure_employees():
    company = frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC"
    emp_map = {}
    for key, spec in EMPLOYEES.items():
        emp_id = frappe.db.get_value("Employee", {"first_name": spec["first_name"], "last_name": spec["last_name"]})
        if not emp_id:
            doc_dict = {
                "doctype": "Employee",
                "first_name": spec["first_name"],
                "last_name": spec["last_name"],
                "employee_name": spec["employee_name"],
                "gender": spec["gender"],
                "date_of_birth": spec["date_of_birth"],
                "date_of_joining": spec["date_of_joining"],
                "status": spec["status"],
                "designation": "Technician",
                "company": company
            }
            if spec.get("relieving_date"):
                doc_dict["relieving_date"] = spec["relieving_date"]
            emp = frappe.get_doc(doc_dict).insert(ignore_permissions=True)
            emp_id = emp.name
        else:
            curr_status = frappe.db.get_value("Employee", emp_id, "status")
            if curr_status != spec["status"]:
                frappe.db.set_value("Employee", emp_id, "status", spec["status"])
        emp_map[key] = emp_id
    return emp_map

def ensure_items():
    for item_code, data in ITEMS.items():
        if not frappe.db.exists("Item", item_code):
            doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": data["item_code"],
                "item_name": data["item_name"],
                "description": data.get("description", data["item_name"]),
                "item_group": data["item_group"],
                "is_stock_item": data["is_stock_item"],
                "is_sales_item": data["is_sales_item"],
                "stock_uom": data["stock_uom"],
                "custom_frt": data["custom_frt"],
                "uoms": [{"uom": "Hour", "conversion_factor": 1.0}]
            })
            doc.insert(ignore_permissions=True)
        else:
            curr_frt = frappe.db.get_value("Item", item_code, "custom_frt")
            if curr_frt != data["custom_frt"]:
                frappe.db.set_value("Item", item_code, "custom_frt", data["custom_frt"])
            item_doc = frappe.get_doc("Item", item_code)
            if not any(u.uom == "Hour" for u in item_doc.uoms):
                item_doc.append("uoms", {"uom": "Hour", "conversion_factor": 1.0})
                item_doc.save(ignore_permissions=True)

def ensure_shop_settings():
    if frappe.db.exists("DocType", "Shop Settings"):
        settings = frappe.get_single("Shop Settings")
        settings.technician_designation = "Technician"
        settings.enable_technician_capacity = 1
        settings.save(ignore_permissions=True)

def create_test_sales_order(po_no, customer=None, item_code=None):
    """Helper to create a transactional Sales Order on demand during test execution."""
    customer = customer or CUSTOMER
    item_code = item_code or f"{PREFIX}SERVICE_001"
    
    so_name = frappe.db.get_value("Sales Order", {"customer": customer, "po_no": po_no})
    if not so_name:
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            "customer": customer,
            "po_no": po_no,
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "items": [{
                "item_code": item_code,
                "qty": 1,
                "rate": 100
            }]
        }).insert(ignore_permissions=True)
        so_name = so.name
    return so_name

def teardown_transactional(employee_ids=None):
    """Cleans up transactional test entries (Schedule Entries, Leave Applications, Sales Orders) created during tests."""
    frappe.db.sql("DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE %s OR sales_order IN (SELECT name FROM `tabSales Order` WHERE customer LIKE %s)", (f"{PREFIX}%", f"{PREFIX}%"))
    frappe.db.sql("DELETE FROM `tabSales Order` WHERE customer = %s OR po_no LIKE %s", (CUSTOMER, f"{PREFIX}%"))
    if employee_ids:
        frappe.db.sql("DELETE FROM `tabLeave Application` WHERE employee IN (%s)" % ", ".join(["%s"] * len(employee_ids)), tuple(employee_ids))
    frappe.db.commit()
