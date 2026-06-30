import frappe
from frappe import _

def override_dashboard(data=None):
	if not data or not data.get("transactions"):
		return data

	items_to_remove = ["Project Update", "Material Request", "BOM", "Work Order"]
	items_to_move_to_purchase = ["Expense Claim"]
	items_to_move_to_project = ["Stock Entry"]
	
	all_removals = items_to_remove + items_to_move_to_purchase + items_to_move_to_project

	# Filter out unwanted items from all transaction groups
	for group in data.get("transactions", []):
		if group.get("items"):
			group["items"] = [item for item in group["items"] if item not in all_removals]

	purchase_group = None
	sales_group = None
	project_group = None

	for group in data.get("transactions", []):
		label = group.get("label")
		if label in ("Purchase", _("Purchase")):
			purchase_group = group
		elif label in ("Sales", _("Sales")):
			sales_group = group
		elif label in ("Project", _("Project")):
			project_group = group

	if purchase_group is not None:
		purchase_group["items"].extend(["Expense Claim"])
	else:
		data["transactions"].append({
			"label": _("Purchase"),
			"items": ["Expense Claim"]
		})

	if project_group is not None:
		project_group["items"].extend(["Stock Entry"])
	else:
		data["transactions"].insert(0, {
			"label": _("Project"),
			"items": ["Stock Entry"]
		})

	if sales_group is not None:
		# Remove these items if they exist to prevent duplicates, then prepend in desired order
		for item in ["Quotation", "Sales Order", "Sales Invoice", "Delivery Note"]:
			if item in sales_group["items"]:
				sales_group["items"].remove(item)
		sales_group["items"] = ["Quotation", "Sales Order", "Sales Invoice", "Delivery Note"] + sales_group["items"]
	else:
		data["transactions"].append({
			"label": _("Sales"),
			"items": ["Quotation", "Sales Order", "Sales Invoice", "Delivery Note"]
		})

	# Remove any groups that are now empty
	data["transactions"] = [group for group in data.get("transactions", []) if group.get("items")]

	return data
