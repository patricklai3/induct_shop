import frappe
from induct_shop.install import seed_schedule_entry_types

PREFIX = "Test "

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

REPAIR_VEHICLE_MODEL_S = {
    "vin": "5YJSA1E69PF123456"
}

REPAIR_VEHICLE_MODEL_Y = {
    "vin": "5YJYGDEE9PF123456"
}

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
    ensure_company()
    ensure_fiscal_year()
    ensure_price_list()
    ensure_gender()
    ensure_uom()
    ensure_item_groups()
    ensure_equipment_tags()
    ensure_service_bays()
    ensure_customer()
    ensure_repair_vehicles()
    ensure_designation()
    emp_map = ensure_employees()
    ensure_items()
    ensure_shop_settings()
    seed_schedule_entry_types()
    frappe.db.commit()
    return emp_map


def ensure_uom():
    for uom_name in ["Hour", "Nos"]:
        if not frappe.db.exists("UOM", uom_name):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom_name}).insert(ignore_permissions=True)

def ensure_company():
    company_name = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company_name or company_name == "i" or not frappe.db.exists("Company", company_name):
        company_name = "Wind Power LLC"
        if not frappe.db.exists("Company", company_name):
            frappe.get_doc({
                "doctype": "Company",
                "company_name": company_name,
                "abbr": "WP",
                "default_currency": "USD",
                "country": "United States"
            }).insert(ignore_permissions=True)
    frappe.db.set_single_value("Global Defaults", "default_company", company_name)
    frappe.defaults.set_user_default("company", company_name)
    frappe.defaults.set_global_default("company", company_name)
    return company_name

def ensure_fiscal_year():
    company = ensure_company()
    for year_val in [2025, 2026, 2027]:
        year_name = str(year_val)
        if not frappe.db.exists("Fiscal Year", year_name):
            frappe.get_doc({
                "doctype": "Fiscal Year",
                "year": year_name,
                "year_start_date": f"{year_val}-01-01",
                "year_end_date": f"{year_val}-12-31",
                "companies": [{"company": company}]
            }).insert(ignore_permissions=True)

def ensure_gender():
    for g in ["Male", "Female", "Other"]:
        if not frappe.db.exists("Gender", g):
            frappe.get_doc({
                "doctype": "Gender",
                "gender": g
            }).insert(ignore_permissions=True)

def ensure_employees():
    company = ensure_company()
    ensure_gender()
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

def ensure_item_groups():
    if not frappe.db.exists("Item Group", "All Item Groups"):
        frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": "All Item Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
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
    legacy_bays = frappe.db.sql("SELECT name FROM `tabService Bay` WHERE name LIKE '_IST_%%' OR name IN ('1', '2')", pluck=True)
    for b in legacy_bays:
        frappe.delete_doc("Service Bay", b, force=True, ignore_permissions=True)

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
            bay_doc = frappe.get_doc("Service Bay", bay_name)
            updated = False
            if bay_doc.is_active != data["is_active"]:
                bay_doc.is_active = data["is_active"]
                updated = True
            expected_tags = {e["equipment_tag"] for e in data["equipment"]}
            existing_tags = {e.equipment_tag for e in bay_doc.equipment}
            if expected_tags != existing_tags:
                bay_doc.set("equipment", data["equipment"])
                updated = True
            if updated:
                bay_doc.save(ignore_permissions=True)

def ensure_customer():
    if not frappe.db.exists("Customer Group", "All Customer Groups"):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "All Customer Groups",
            "is_group": 1
        }).insert(ignore_permissions=True)
    for cg in ["Commercial", "Individual"]:
        if not frappe.db.exists("Customer Group", cg):
            frappe.get_doc({
                "doctype": "Customer Group",
                "customer_group_name": cg,
                "parent_customer_group": "All Customer Groups"
            }).insert(ignore_permissions=True)
    if not frappe.db.exists("Territory", "All Territories"):
        frappe.get_doc({
            "doctype": "Territory",
            "territory_name": "All Territories",
            "is_group": 1
        }).insert(ignore_permissions=True)
    if not frappe.db.exists("Customer", CUSTOMER):
        frappe.get_doc({
            "doctype": "Customer",
            "customer_name": CUSTOMER,
            "customer_group": "Commercial",
            "territory": "All Territories"
        }).insert(ignore_permissions=True)

def ensure_repair_vehicles():
    for spec in [REPAIR_VEHICLE_MODEL_S, REPAIR_VEHICLE_MODEL_Y]:
        vin = spec["vin"]
        if not frappe.db.exists("Repair Vehicle", vin):
            frappe.get_doc({
                "doctype": "Repair Vehicle",
                "vin": vin,
                "customer": CUSTOMER
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

def ensure_price_list():
    if not frappe.db.exists("Price List", "Standard Selling"):
        frappe.get_doc({
            "doctype": "Price List",
            "price_list_name": "Standard Selling",
            "selling": 1,
            "currency": "USD"
        }).insert(ignore_permissions=True)

def create_test_sales_order(po_no, customer=None, item_code=None):
    """Helper to create a transactional Sales Order on demand during test execution."""
    customer = customer or CUSTOMER
    item_code = item_code or f"{PREFIX}SERVICE_001"
    ensure_price_list()
    
    so_name = frappe.db.get_value("Sales Order", {"customer": customer, "po_no": po_no})
    if not so_name:
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "company": frappe.db.get_single_value("Global Defaults", "default_company") or "Wind Power LLC",
            "customer": customer,
            "po_no": po_no,
            "currency": "USD",
            "selling_price_list": "Standard Selling",
            "price_list_currency": "USD",
            "plc_conversion_rate": 1.0,
            "conversion_rate": 1.0,
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 1),
            "items": [{
                "item_code": item_code,
                "qty": 1,
                "rate": 100
            }]
        }).insert(ignore_permissions=True)
        so_name = so.name
    return so_name

def create_test_vehicle_check_in(customer=None, vehicle=None, schedule_entry=None):
    """Helper to create a transactional Vehicle Check-in on demand during test execution."""
    customer = customer or CUSTOMER
    vehicle = vehicle or REPAIR_VEHICLE_MODEL_S["vin"]
    vci = frappe.get_doc({
        "doctype": "Vehicle Check-in",
        "customer": customer,
        "vehicle": vehicle,
        "schedule_entry": schedule_entry,
        "intake_mileage": 10000,
        "check_in_date": frappe.utils.now_datetime()
    }).insert(ignore_permissions=True)
    return vci

def teardown_transactional(employee_ids=None):
    """Cleans up ALL transactional test entries created during tests."""
    # 1. Vehicle Check-in (before Project due to link)
    frappe.db.sql(
        "DELETE FROM `tabVehicle Check-in` WHERE customer LIKE %s OR customer LIKE %s",
        (f"{PREFIX}%", "_Test%")
    )
    # 2. Schedule Entry
    frappe.db.sql(
        "DELETE FROM `tabSchedule Entry` WHERE service_bay LIKE %s "
        "OR service_bay = 'Test Schedule Bay' "
        "OR sales_order IN (SELECT name FROM `tabSales Order` WHERE customer LIKE %s OR customer LIKE %s)",
        (f"{PREFIX}%", f"{PREFIX}%", "_Test%")
    )
    # 3. Project (after VCI and SE which may link to it)
    frappe.db.sql(
        "DELETE FROM `tabProject` WHERE customer LIKE %s OR customer LIKE %s OR name LIKE %s",
        (f"{PREFIX}%", "_Test%", "Project TESTVIN%")
    )
    # 4. Sales Order
    frappe.db.sql(
        "DELETE FROM `tabSales Order` WHERE customer = %s OR customer LIKE %s OR po_no LIKE %s",
        (CUSTOMER, "_Test%", f"{PREFIX}%")
    )
    # 5. Repair Vehicle ad-hoc cleanup
    frappe.db.sql(
        "DELETE FROM `tabRepair Vehicle` WHERE name LIKE %s",
        ("TESTVIN%",)
    )
    # 6. Leave Application
    if employee_ids:
        frappe.db.sql(
            "DELETE FROM `tabLeave Application` WHERE employee IN (%s)"
            % ", ".join(["%s"] * len(employee_ids)),
            tuple(employee_ids)
        )
    frappe.db.commit()


def count_test_records():
    """Returns record counts for all test transactional records in the database."""
    vci_count = frappe.db.sql("SELECT count(*) FROM `tabVehicle Check-in` WHERE customer LIKE %s OR customer LIKE %s", (f"{PREFIX}%", "_Test%"))[0][0]
    project_count = frappe.db.sql("SELECT count(*) FROM `tabProject` WHERE customer LIKE %s OR customer LIKE %s", (f"{PREFIX}%", "_Test%"))[0][0]
    se_count = frappe.db.sql("SELECT count(*) FROM `tabSchedule Entry` WHERE service_bay LIKE %s OR service_bay = 'Test Schedule Bay'", (f"{PREFIX}%",))[0][0]
    so_count = frappe.db.sql("SELECT count(*) FROM `tabSales Order` WHERE customer = %s OR customer LIKE %s", (CUSTOMER, "_Test%"))[0][0]
    print(f"RESIDUAL_RECORDS_CHECK -> VCI: {vci_count}, Project: {project_count}, SE: {se_count}, SO: {so_count}")
    return {"vci": vci_count, "project": project_count, "se": se_count, "so": so_count}


