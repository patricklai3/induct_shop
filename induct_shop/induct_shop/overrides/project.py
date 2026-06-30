import frappe
from frappe.utils import flt
from erpnext.projects.doctype.project.project import Project

class CustomProject(Project):
    def update_costing(self):
        super().update_costing()
        
        # 1. Delivery Note & Sales Invoice Cost (Outgoing Stock)
        out_cost = frappe.db.sql("""
            select sum(stock_value_difference)
            from `tabStock Ledger Entry`
            where project = %s 
            and is_cancelled = 0
            and voucher_type in ('Delivery Note', 'Sales Invoice')
        """, self.name)[0][0] or 0
        
        self.custom_sales_stock_cost = -1 * flt(out_cost)
        
        # 2. Material Receipt Value (Incoming Stock)
        in_value = frappe.db.sql("""
            select sum(sle.stock_value_difference)
            from `tabStock Ledger Entry` sle
            join `tabStock Entry` se on sle.voucher_no = se.name
            where sle.project = %s
            and sle.is_cancelled = 0
            and sle.voucher_type = 'Stock Entry'
            and se.purpose = 'Material Receipt'
        """, self.name)[0][0] or 0
        
        self.custom_incoming_material_value = flt(in_value)
        
        # Re-calculate gross margin with the new fields
        self.calculate_gross_margin()

    def calculate_gross_margin(self):
        expense_amount = (
            flt(self.total_costing_amount)
            + flt(self.total_purchase_cost)
            + flt(self.get("total_consumed_material_cost", 0))
            + flt(self.get("custom_sales_stock_cost", 0))
            - flt(self.get("custom_incoming_material_value", 0))
        )
        
        self.gross_margin = flt(self.total_billed_amount) - expense_amount
        if self.total_billed_amount:
            self.per_gross_margin = (self.gross_margin / flt(self.total_billed_amount)) * 100
        else:
            self.per_gross_margin = 0


def update_project_costing(doc, method):
    projects = set()
    if doc.get("project"):
        projects.add(doc.project)
    
    for item in doc.get("items", []):
        if item.get("project"):
            projects.add(item.project)
    
    for project in projects:
        frappe.enqueue(
            "erpnext.projects.doctype.project.project.update_costing_and_billing",
            project=project
        )
