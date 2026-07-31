import frappe

def get_context(context):
	context.boot = frappe._dict(
		boot=frappe.website.utils.get_boot_data()
	)
	return context
