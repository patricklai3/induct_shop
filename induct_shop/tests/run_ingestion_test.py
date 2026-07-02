import frappe
from induct_shop.api.service_parts_selector import ingest_part, ingest_service

TEST_PARTS = """1083401-05-O	INSTRUMENT PANEL - SUBASSEMBLY		Model 3 Jun 2017 - Dec 2023	14 - INSTRUMENT PANEL	1405 - Instrument Panel	Dash Panel
1083401-05-O	INSTRUMENT PANEL - SUBASSEMBLY		Model Y Jan 2020 - Jan 2025	14 - INSTRUMENT PANEL	1405 - Instrument Panel	Dash Panel
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model Y Jan 2020 - Jan 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model 3 Jun 2017 - Dec 2023	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188354-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - LEFT HAND	FR LWR COMP LINK ASSY, CN, LH	Model 3 Jan 2024	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188354-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - LEFT HAND	FR LWR COMP LINK ASSY, CN, LH	Model Y Feb 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model Y Feb 2025	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
2188359-10-B	FRONT LOWER COMPLIANCE LINK ASSEMBLY - RIGHT HAND	FR LWR COMP LINK ASSY, CN, RH	Model 3 Jan 2024	31 - SUSPENSION	3101 - Front Suspension (including Hubs)	Front Suspension Arms
"""

SERVICE_URLS = [
    "https://service.tesla.com/docs/Model3/ServiceManual/en-us/GUID-DE61971B-D5F1-4C5C-9050-DE313445276D.html",
    "https://service.tesla.com/docs/ModelY/ServiceManual/2025/en-us/GUID-0101FEE3-AEA9-4EC3-818F-06EC67D95830.html"
]

def run_tests():
    print("Running Part Ingestion Test...")
    part_results = ingest_part(TEST_PARTS)
    print("Part Ingestion Results:")
    for res in part_results:
        print(f" - {res}")
        
    print("\nVerifying Deduplication for Part 1083401 (Instrument Panel)...")
    item = frappe.get_doc("Item", "1083401")
    print(f"Models for 1083401: {[d.model for d in item.custom_model_compatibility]}")

    print("\nRunning Service Ingestion Test...")
    for url in SERVICE_URLS:
        try:
            print(f"Fetching {url}")
            res = ingest_service(url)
            print(f" - Ingested Service: {res}")
        except Exception as e:
            print(f" - Error fetching {url}: {e}")
            
    print("\nAll tests completed.")
    
if __name__ == "__main__":
    frappe.init(site="development.localhost", sites_path="sites")
    frappe.connect()
    try:
        run_tests()
    finally:
        frappe.destroy()
