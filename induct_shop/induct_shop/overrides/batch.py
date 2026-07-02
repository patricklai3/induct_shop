import frappe
from frappe.model.document import Document

def autoname(doc, method=None):
    """
    Automatically generates the Batch ID in the format:
    #######-##-X-XXX-XXX (e.g., 1234567-00-D-AFT-NEW or 1234567-00-D-OEM-USD)
    combining Item Code, Revision, OEM Status, and Condition.
    """
    # Use standard autoname if this batch doesn't have our custom fields set
    if not (doc.custom_revision_suffix and doc.custom_condition and doc.custom_oem_status):
        return
        
    item_code = doc.item
    
    # Ensure item_code is strings and available
    if not item_code:
        return

    # E.g. revision_suffix is expected to be "-00-C" or similar.
    # OEM Status: "OEM" -> "OEM", "Aftermarket" -> "AFT"
    oem_abbr = "OEM" if doc.custom_oem_status == "OEM" else "AFT"
    
    # Condition: "New" -> "NEW", "Used" -> "USD", "Reconditioned" -> "REC"
    condition_abbr = "NEW"
    if doc.custom_condition == "Used":
        condition_abbr = "USD"
    elif doc.custom_condition == "Reconditioned":
        condition_abbr = "REC"
        
    # Example format: 1974875-00-C-AFT-NEW
    # We assume custom_revision_suffix contains the leading dash, e.g. "-00-C".
    suffix = doc.custom_revision_suffix
    if not suffix.startswith("-"):
        suffix = "-" + suffix
        
    batch_id = f"{item_code}{suffix}-{oem_abbr}-{condition_abbr}"
    
    doc.name = batch_id
