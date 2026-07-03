import frappe
from frappe import _
import requests
from bs4 import BeautifulSoup
import re

@frappe.whitelist()
def search_catalog(query, doc_type=None, project=None):
    """
    Searches for items (parts) and services.
    Returns list of matching items with their prices and stock availability.
    If doc_type is a stock/procurement doc, filter out services.
    """
    filters = [
        ["Item", "item_code", "like", f"%{query}%"],
        ["Item", "item_name", "like", f"%{query}%"]
    ]
    
    # If opened from a Stock document, hide services
    is_stock_doc = doc_type in ["Purchase Receipt", "Stock Entry"]
    
    vehicle_model = None
    if project:
        project_doc = frappe.get_cached_doc("Project", project)
        vehicle_model = project_doc.get("custom_vehicle_model")
    
    items = frappe.get_all("Item", 
        or_filters=filters,
        fields=["item_code", "item_name", "description", "item_group", "is_stock_item", "custom_frt"],
        limit=100
    )
    
    results = []
    for item in items:
        if is_stock_doc and not item.is_stock_item:
            continue
            
        # Model Compatibility Filtering
        if vehicle_model:
            item_compats = frappe.get_all("Model Compatibility", filters={"parent": item.item_code, "parenttype": "Item"}, fields=["model"])
            if item_compats:
                # If this item has specified compatible models, ensure our vehicle model is one of them
                if not any(c.model == vehicle_model for c in item_compats):
                    continue
            
        # Get stock and pricing based on batches if it's a part
        batches = []
        if item.is_stock_item:
            batch_records = frappe.get_all("Batch", filters={"item": item.item_code}, fields=["name", "custom_condition", "custom_oem_status", "custom_revision_suffix"])
            batches = batch_records
            
        results.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "description": item.description,
            "is_stock_item": item.is_stock_item,
            "custom_frt": item.custom_frt,
            "batches": batches
        })
        
        if len(results) >= 20:
            break
        
    return results

@frappe.whitelist()
def ingest_part(payload):
    """
    Ingests parts from tab-delimited text.
    payload: string containing the tab-delimited text.
    """
    lines = payload.strip().split('\n')
    results = []
    
    for line in lines:
        if not line.strip(): continue
        
        parts = line.split('\t')
        if len(parts) < 6:
            continue
            
        # Example: 1083401-05-O \t INSTRUMENT PANEL - SUBASSEMBLY \t \t Model 3 Jun 2017 - Dec 2023 \t 14 - INSTRUMENT PANEL \t 1405 - Instrument Panel \t Dash Panel
        
        raw_part_no = parts[0].strip()
        name = parts[1].strip()
        description = parts[2].strip() if len(parts) > 2 else ""
        model_str = parts[3].strip() if len(parts) > 3 else ""
        category_str = parts[4].strip() if len(parts) > 4 else ""
        subcategory_str = parts[5].strip() if len(parts) > 5 else ""
        group_str = parts[6].strip() if len(parts) > 6 else ""

        # Base part number usually first 7 digits
        base_part_match = re.match(r"^(\d{7})", raw_part_no)
        base_part_no = base_part_match.group(1) if base_part_match else raw_part_no
        
        revision = raw_part_no[len(base_part_no):]
        
        # Build Item Group Tree
        parent_group = "Tesla"
        _ensure_item_group(parent_group, "All Item Groups")
        
        if category_str:
            parent_group = _ensure_item_group(category_str, parent_group)
            
        if subcategory_str:
            parent_group = _ensure_item_group(subcategory_str, parent_group)
            
        if group_str:
            parent_group = _ensure_item_group(group_str, parent_group)
            
        # Create or Update Item
        if not frappe.db.exists("Item", base_part_no):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": base_part_no,
                "item_name": name,
                "description": description or name,
                "item_group": parent_group,
                "is_stock_item": 1,
                "has_batch_no": 1,
                "stock_uom": "Unit",
                "custom_model_compatibility": []
            })
            item.insert(ignore_permissions=True)
        else:
            item = frappe.get_doc("Item", base_part_no)
            
        # Append Model Compatibility (Deduplicate)
        model, date_range = _parse_model_string(model_str)
        if model:
            exists = any(d.model == model and d.date_range == date_range for d in item.custom_model_compatibility)
            if not exists:
                item.append("custom_model_compatibility", {
                    "model": model,
                    "date_range": date_range
                })
                item.save(ignore_permissions=True)
                
        # Create Batch
        # Note: Condition and OEM Status should ideally be provided by the user in the UI before calling ingest, but for now we default to 'New' and 'OEM'.
        condition = "New"
        oem_status = "OEM"
        batch_id = f"{base_part_no}{revision}-{oem_status[:3].upper()}-{condition[:3].upper()}"
        
        if not frappe.db.exists("Batch", batch_id):
            batch = frappe.get_doc({
                "doctype": "Batch",
                "batch_id": batch_id,
                "item": base_part_no,
                "custom_revision_suffix": revision,
                "custom_condition": condition,
                "custom_oem_status": oem_status
            })
            batch.insert(ignore_permissions=True)
            
        results.append({
            "item_code": base_part_no,
            "batch_id": batch_id,
            "revision": revision
        })
        
    return results

def _ensure_item_group(group_name, parent_name):
    match = re.match(r"^(\d+)\s*-\s*", group_name)
    is_service = "(service)" in group_name
    
    actual_group_name = group_name
    
    if match:
        prefix = match.group(1)
        filters = [["name", "like", f"{prefix} -%"]]
        if is_service:
            filters.append(["name", "like", "%(service)%"])
        else:
            filters.append(["name", "not like", "%(service)%"])
            
        existing = frappe.get_all("Item Group", filters=filters, limit=1)
        if existing:
            actual_group_name = existing[0].name
            
    if not frappe.db.exists("Item Group", actual_group_name):
        doc = frappe.get_doc({
            "doctype": "Item Group",
            "item_group_name": actual_group_name,
            "parent_item_group": parent_name,
            "is_group": 1
        })
        doc.insert(ignore_permissions=True)
        
    return actual_group_name

def _parse_model_string(model_str):
    # e.g., "Model 3 Jun 2017 - Dec 2023" -> ("Model 3", "Jun 2017 - Dec 2023")
    match = re.match(r"(Model\s+[A-Za-z0-9]+)\s*(.*)", model_str)
    if match:
        return match.group(1), match.group(2).strip()
    return model_str, ""

def _get_generations_for_service_url(url):
    generations = []
    
    if "/ModelS/" in url:
        if "/Palladium/" in url:
            generations = ["Model S Feb 2021 - May 2025", "Model S June 2025"]
        else:
            generations = ["Model S Feb 2012 - Mar 2016", "Model S Apr 2016 - Jan 2021"]
    elif "/Model3/" in url:
        if "/2024/" in url:
            generations = ["Model 3 Jan 2024"]
        else:
            generations = ["Model 3 Jun 2017 - Dec 2023"]
    elif "/ModelX/" in url:
        if "/Palladium/" in url:
            generations = ["Model X Mar 2021 - May 2025", "Model X June 2025"]
        else:
            generations = ["Model X Sep 2015 - Feb 2021"]
    elif "/ModelY/" in url:
        if "/2025/" in url:
            generations = ["Model Y Feb 2025"]
        else:
            generations = ["Model Y Jan 2020 - Jan 2025"]
            
    return generations

@frappe.whitelist()
def ingest_service(url):
    """
    Ingests a service from a Tesla Service Manual URL.
    Example URL: https://service.tesla.com/docs/Model3/ServiceManual/en-us/GUID-DE61971B-D5F1-4C5C-9050-DE313445276D.html
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        frappe.throw(_("Could not fetch the service manual: {0}").format(str(e)))
        
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract Title (title tag)
    title_el = soup.find('title')
    title = title_el.text.strip() if title_el else "Unknown Service"
    
    # Extract Correction Code and FRT Value
    correction_code = ""
    frt_value = 0.0
    
    # Look for meta description
    # e.g., <meta name="description" content="Correction code 14052202 3.54 NOTE: ...">
    # or <meta name="description" content="Correction code 2020020012 FRT 0.06 NOTE: ...">
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        content = meta_desc['content']
        match = re.search(r"Correction code\s+(\d+)\s*(?:FRT\s+)?([\d\.]+)", content, re.I)
        if match:
            correction_code = match.group(1)
            try:
                frt_value = float(match.group(2))
            except:
                pass

    if not correction_code:
        # Fallback to general text search
        text = soup.get_text()
        cc_match = re.search(r"Correction Code\s*[:\n]*\s*(\d{7,})", text, re.I)
        if cc_match:
            correction_code = cc_match.group(1)
        frt_match = re.search(r"FRT\s*[:\n]*\s*([\d\.]+)", text, re.I)
        if frt_match:
            try:
                frt_value = float(frt_match.group(1))
            except:
                pass
                
    if not correction_code:
        frappe.throw(_("Could not find Correction Code in the provided manual."))
        
    # Generations from URL
    generations = _get_generations_for_service_url(url)
    
    # Category and Subcategory
    cat_id = correction_code[:2] if len(correction_code) >= 2 else "00"
    subcat_id = correction_code[:4] if len(correction_code) >= 4 else "0000"
    
    cat_name = f"{cat_id} - Unknown (service)"
    subcat_name = f"{subcat_id} - Unknown (service)"
    
    import json
    import os
    json_path = frappe.get_app_path("induct_shop", "data", "tesla_service_categories.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            mapping = json.load(f)
        
        cat_data = mapping.get(cat_id)
        if cat_data:
            cat_name = f"{cat_id} - {cat_data.get('name', 'Unknown')} (service)"
            subcats = cat_data.get("subcategories", {})
            subcat_val = subcats.get(subcat_id)
            if subcat_val:
                subcat_name = f"{subcat_id} - {subcat_val} (service)"
                
    _ensure_item_group("Tesla Services", "All Item Groups")
    cat_name = _ensure_item_group(cat_name, "Tesla Services")
    subcat_name = _ensure_item_group(subcat_name, cat_name)
    
    item_group = subcat_name
    
    if not frappe.db.exists("Item", correction_code):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": correction_code,
            "item_name": title[:140],
            "description": title,
            "item_group": item_group,
            "is_stock_item": 0,
            "is_sales_item": 1,
            "stock_uom": "Hour",
            "custom_frt": frt_value,
            "custom_model_compatibility": []
        })
        for gen in generations:
            model, date_range = _parse_model_string(gen)
            item.append("custom_model_compatibility", {
                "model": model,
                "date_range": date_range
            })
        item.insert(ignore_permissions=True)
    else:
        item = frappe.get_doc("Item", correction_code)
        item.custom_frt = frt_value
        item.item_group = item_group
        for gen in generations:
            model, date_range = _parse_model_string(gen)
            exists = any(d.model == model and d.date_range == date_range for d in item.custom_model_compatibility)
            if not exists:
                item.append("custom_model_compatibility", {
                    "model": model,
                    "date_range": date_range
                })
        item.save(ignore_permissions=True)
        
    return {
        "item_code": correction_code,
        "title": title,
        "frt_value": frt_value,
        "generations": generations
    }

@frappe.whitelist()
def get_smart_suggestions(service_code):
    """
    Returns parts frequently associated with the given service.
    """
    if frappe.db.exists("Service Part Association", service_code):
        doc = frappe.get_doc("Service Part Association", service_code)
        # Sort by frequency descending
        parts = sorted(doc.parts, key=lambda x: x.frequency, reverse=True)
        return [{"part_code": p.part_code, "frequency": p.frequency} for p in parts[:5]]
    return []

@frappe.whitelist()
def update_associations(doc, method=None):
    """
    Background job to learn associations from a submitted sales document.
    """
    if isinstance(doc, str):
        doc = frappe.get_doc(method, doc)
        
    for item in doc.get("items", []):
        is_stock_item = frappe.get_cached_value("Item", item.item_code, "is_stock_item")
        if item.custom_parent_service_reference and is_stock_item:
            service_code = item.custom_parent_service_reference
            part_code = item.item_code
            
            # Check if parent association exists
            if not frappe.db.exists("Service Part Association", service_code):
                assoc = frappe.get_doc({
                    "doctype": "Service Part Association",
                    "service_code": service_code
                })
                assoc.insert(ignore_permissions=True)
            else:
                assoc = frappe.get_doc("Service Part Association", service_code)
                
            # Check if part already exists in child table
            existing_part = next((p for p in assoc.parts if p.part_code == part_code), None)
            
            if existing_part:
                existing_part.frequency += 1
            else:
                assoc.append("parts", {
                    "part_code": part_code,
                    "frequency": 1
                })
                
            assoc.save(ignore_permissions=True)

def auto_assign_parent_services(doc, method=None):
    """
    Automatically associates parts with the nearest preceding service by row order.
    Triggered on validate of Quotation, Sales Order, and Sales Invoice.
    """
    last_service_code = None
    
    sorted_items = sorted(doc.get("items", []), key=lambda x: x.idx)
    
    for item in sorted_items:
        is_stock_item = frappe.get_cached_value("Item", item.item_code, "is_stock_item")
        if not is_stock_item:
            last_service_code = item.item_code
        else:
            if last_service_code and not item.custom_parent_service_reference:
                item.custom_parent_service_reference = last_service_code
