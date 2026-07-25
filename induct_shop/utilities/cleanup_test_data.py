import frappe

def run():
    """Cleanup legacy ununified test data from the database."""
    print("Cleaning up legacy test master data and transactional records...")

    # 1. Schedule Entries linked to old test bays or customers
    frappe.db.sql("""
        DELETE FROM `tabSchedule Entry`
        WHERE service_bay LIKE 'Test Bay%'
           OR service_bay LIKE 'Test Tech Bay%'
           OR sales_order IN (
               SELECT name FROM `tabSales Order`
               WHERE customer LIKE '_Test%'
           )
    """)

    # 2. Sales Orders for legacy test customers
    frappe.db.sql("""
        DELETE FROM `tabSales Order`
        WHERE customer LIKE '_Test%'
           OR po_no LIKE 'SO-SCHED-%'
           OR po_no LIKE 'SO-TECH-%'
    """)

    # 3. Legacy Customers
    frappe.db.sql("DELETE FROM `tabCustomer` WHERE customer_name LIKE '_Test%'")

    # 4. Legacy Service Bays
    frappe.db.sql("""
        DELETE FROM `tabService Bay`
        WHERE bay_name LIKE 'Test Bay%'
           OR bay_name LIKE 'Test Tech Bay%'
    """)

    # 5. Legacy Employees
    legacy_emp_ids = frappe.get_all("Employee", filters={"first_name": "Tech"}, pluck="name")
    if legacy_emp_ids:
        frappe.db.sql("DELETE FROM `tabLeave Application` WHERE employee IN (%s)" % ", ".join(["%s"] * len(legacy_emp_ids)), tuple(legacy_emp_ids))
        frappe.db.sql("DELETE FROM `tabEmployee` WHERE name IN (%s)" % ", ".join(["%s"] * len(legacy_emp_ids)), tuple(legacy_emp_ids))

    # 6. Legacy Items
    frappe.db.sql("""
        DELETE FROM `tabItem`
        WHERE item_code IN ('_Test Service Item 01', 'TEST_SERVICE_001', 'EST_TEST_ITEM_001', 'EST_TEST_ITEM_002')
    """)

    frappe.db.commit()
    print("Legacy test data cleanup complete!")
