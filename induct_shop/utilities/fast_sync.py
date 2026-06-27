import frappe
from frappe.model.sync import sync_for
from frappe.utils.fixtures import sync_fixtures

def run():
    print("Fast Syncing Induct Shop...")
    
    # 1. Sync standard DocTypes from module folders
    print("Syncing Standard DocTypes...")
    sync_for("induct_shop")
    
    # 2. Sync Custom Fields & Property Setters
    # Note: Uncomment if you add setup/install.py with an after_migrate hook
    # print("Syncing Custom Fields and Property Setters...")
    # try:
    #     from induct_shop.setup.install import after_migrate
    #     after_migrate()
    # except ImportError:
    #     pass
    
    # 3. Sync Fixtures
    print("Syncing Fixtures...")
    sync_fixtures(app="induct_shop")
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Fast Sync Complete!")
