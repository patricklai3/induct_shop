import sys
import logging

try:
    import frappe
except ImportError:
    frappe = None

logger = logging.getLogger(__name__)

BENCHMARK_URLS = [
    # Mobile Capable (Expected: True)
    ("https://service.tesla.com/docs/ModelX/ServiceManual/en-us/GUID-1CE62E78-7421-47E9-9E5A-40745063F7EE.html", True),
    ("https://service.tesla.com/docs/ModelX/ServiceManual/Palladium/en-us/GUID-DDB0A991-D2AD-49DD-A341-F45E8A9DA5B1.html", True),
    ("https://service.tesla.com/docs/Model3/ServiceManual/2024/en-us/GUID-B277DF62-E18C-4760-A2D4-14E37F5B1E20.html", True),
    # Not Mobile Capable (Expected: False)
    ("https://service.tesla.com/docs/ModelX/ServiceManual/en-us/GUID-5BDD6C6A-0169-49F7-844F-F7F1E76212C7.html", False),
    ("https://service.tesla.com/docs/ModelX/ServiceManual/Palladium/en-us/GUID-583D6569-850E-4113-9687-9AA573C047BA.html", False),
    ("https://service.tesla.com/docs/Model3/ServiceManual/en-us/GUID-04B7BB27-4A36-4546-A9F9-535AFB0B9265.html", False),
    ("https://service.tesla.com/docs/Model3/ServiceManual/2024/en-us/GUID-24F70C5B-9CBA-4D77-AB8A-C5FC2B472A37.html", False),
]

def extract_mobile_capability(url: str, timeout_ms: int = 5000) -> bool:
    """
    Extracts whether a Tesla Service Manual procedure URL is Mobile Capable.

    Because '.mobile-capable-indicator' is dynamically injected via client-side JS,
    this function uses Playwright to wait up to timeout_ms for the indicator element inside 'p.shortdesc'.

    Args:
        url (str): The Tesla service manual procedure page URL.
        timeout_ms (int): Maximum wait time in milliseconds for selector attached event.

    Returns:
        bool: True if Mobile Capable indicator is detected, False otherwise.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        err_msg = "Playwright python package is not installed. Please run 'pip install playwright && playwright install chromium'."
        if frappe and hasattr(frappe, "db") and frappe.db:
            try:
                frappe.log_error(err_msg, "Mobile Capability Extractor")
            except Exception:
                pass
        else:
            logger.error(err_msg)
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                # Wait for indicator element or timeout
                page.wait_for_selector(
                    "p.shortdesc .mobile-capable-indicator, .mobile-capable-indicator",
                    state="attached",
                    timeout=timeout_ms
                )

                # Check text chips for exact 'Mobile Capable' match (and not 'Not Mobile Capable')
                chip_texts = [el.inner_text().strip() for el in page.locator(".mobile-capable-indicator .tds-chip-text, p.shortdesc .tds-chip-text").all()]
                
                # Check img src/alt
                img_srcs = [el.get_attribute("src") or "" for el in page.locator(".mobile-capable-indicator img").all()]
                img_alts = [el.get_attribute("alt") or "" for el in page.locator(".mobile-capable-indicator img").all()]

                is_mobile_capable = False
                
                # Exact matching logic (accounting for 'icon-not-mobile-capable.svg' vs 'icon-mobile-capable.svg')
                if "Mobile Capable" in chip_texts and "Not Mobile Capable" not in chip_texts:
                    is_mobile_capable = True
                elif any("icon-mobile-capable.svg" in s and "icon-not-mobile-capable.svg" not in s for s in img_srcs):
                    is_mobile_capable = True
                elif any(a.strip() == "Mobile Capable" for a in img_alts):
                    is_mobile_capable = True

                browser.close()
                return is_mobile_capable
            except Exception:
                browser.close()
                return False

    except Exception as e:
        err_msg = f"Error extracting mobile capability for {url}: {type(e).__name__} - {str(e)}"
        if frappe and hasattr(frappe, "db") and frappe.db:
            try:
                frappe.log_error(err_msg, "Mobile Capability Extractor")
            except Exception:
                pass
        else:
            logger.error(err_msg)
        return False

def run_benchmark():
    """
    Runs extraction benchmark over all 7 test URLs and prints summary.
    """
    print("=" * 80)
    print("Running Mobile Capability Extraction Benchmark")
    print("=" * 80)

    passed = 0
    total = len(BENCHMARK_URLS)

    for idx, (url, expected) in enumerate(BENCHMARK_URLS, 1):
        print(f"\n[{idx}/{total}] Testing: {url}")
        print(f"Expected: {'Mobile Capable' if expected else 'Not Mobile Capable'}")
        
        result = extract_mobile_capability(url)
        print(f"Result:   {'Mobile Capable' if result else 'Not Mobile Capable'}")

        if result == expected:
            print("Status:   PASSED [OK]")
            passed += 1
        else:
            print("Status:   FAILED [MISMATCH]")

    print("\n" + "=" * 80)
    print(f"Benchmark Summary: {passed}/{total} Passed ({passed/total*100:.1f}%)")
    print("=" * 80)
    return passed == total

if __name__ == "__main__":
    success = run_benchmark()
    sys.exit(0 if success else 1)
