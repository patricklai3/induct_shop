import frappe
from frappe import _
from frappe.model.document import Document
from induct_shop.api.estimation_service import get_total_estimate


class ScheduleEntry(Document):
    def before_insert(self):
        self.populate_from_sales_order()

    def validate(self):
        self.validate_unique_sales_order()

    def populate_from_sales_order(self):
        if not self.sales_order:
            return

        if not frappe.db.exists("Sales Order", self.sales_order):
            return

        so_doc = frappe.get_doc("Sales Order", self.sales_order)

        # 1. Fetch Customer
        if not self.customer:
            self.customer = getattr(so_doc, "customer", None)

        # 2. Fetch Project
        if not self.project:
            project = getattr(so_doc, "project", None)
            if not project:
                project = frappe.db.get_value("Project", {"sales_order": self.sales_order})
            if not project:
                project = frappe.db.get_value(
                    "Sales Order Item",
                    {"parent": self.sales_order, "project": ["is", "set"]},
                    "project",
                )
            self.project = project

        # 3. Fetch Repair Vehicle (primarily from linked Project)
        if not self.repair_vehicle:
            vehicle = None
            if self.project:
                if frappe.db.has_column("Project", "custom_repair_vehicle"):
                    vehicle = frappe.db.get_value("Project", self.project, "custom_repair_vehicle")
                elif frappe.db.has_column("Project", "repair_vehicle"):
                    vehicle = frappe.db.get_value("Project", self.project, "repair_vehicle")

            if not vehicle:
                if frappe.db.has_column("Sales Order", "custom_repair_vehicle"):
                    vehicle = getattr(so_doc, "custom_repair_vehicle", None)
                elif frappe.db.has_column("Sales Order", "repair_vehicle"):
                    vehicle = getattr(so_doc, "repair_vehicle", None)

            self.repair_vehicle = vehicle

        # 4. Auto-calculate estimated_duration using get_total_estimate() with Sales Order items
        if not self.estimated_duration:
            operations = []
            for item in getattr(so_doc, "items", []):
                code = getattr(item, "item_code", None)
                if not code:
                    continue

                frt_hours = None
                # Priority 1: Line item custom_frt override
                if hasattr(item, "custom_frt") and item.custom_frt:
                    try:
                        val = float(item.custom_frt)
                        if val > 0:
                            frt_hours = val
                    except (ValueError, TypeError):
                        pass

                # Priority 2: Line item qty (when specified in Hours or for service/non-stock items)
                if frt_hours is None and hasattr(item, "qty") and item.qty:
                    try:
                        qty_val = float(item.qty)
                        uom = getattr(item, "uom", "") or getattr(item, "stock_uom", "")
                        is_hour_uom = str(uom).lower() in ("hour", "hours", "hr", "hrs")
                        is_non_stock = False
                        if frappe.db.exists("Item", code):
                            is_non_stock = not frappe.db.get_value("Item", code, "is_stock_item")

                        if (is_hour_uom or is_non_stock) and qty_val > 0:
                            frt_hours = qty_val
                    except (ValueError, TypeError):
                        pass

                if frt_hours is not None:
                    operations.append({
                        "item_code": code,
                        "flat_rate_hours": frt_hours
                    })
                else:
                    operations.append(code)

            if operations:
                self.estimated_duration = get_total_estimate(operations)
            else:
                self.estimated_duration = 0

        # 5. Auto-generate items_summary from SO items
        if not self.items_summary and hasattr(so_doc, "items"):
            summary_lines = []
            for item in so_doc.items:
                code = getattr(item, "item_code", "")
                name = getattr(item, "item_name", "")
                qty = getattr(item, "qty", 1)
                name_part = f" - {name}" if name and name != code else ""
                summary_lines.append(f"• {code}{name_part} (Qty: {qty})")
            self.items_summary = "\n".join(summary_lines)

    def validate_unique_sales_order(self):
        if not self.sales_order:
            return

        existing = frappe.db.get_value(
            "Schedule Entry",
            {"sales_order": self.sales_order, "name": ["!=", self.name or ""]},
        )
        if existing:
            frappe.throw(
                _("A Schedule Entry ({0}) already exists for Sales Order {1}.").format(existing, self.sales_order),
                frappe.DuplicateEntryError,
            )
