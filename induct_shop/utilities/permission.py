import frappe

def check_app_permission():
	"""Check if current user has permission to access Induct Shop application."""
	if frappe.session.user == "Guest":
		return False
	return True
