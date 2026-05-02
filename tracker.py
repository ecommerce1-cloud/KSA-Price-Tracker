import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from datetime import datetime
import os
import time

API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_price_stealth(browser, barcode, platform):
    urls = {
        "noon": f"https://www.noon.com/saudi-en/search/?q={barcode}",
        "hungerstation": f"https://hungerstation.com/sa-en/search?q={barcode}",
        "ninja": f"https://aswaqninja.com/search?q={barcode}",
        "keeta": f"https://www.keeta.com/sa/search?q={barcode}"
    }
    
    # We use ScraperAnt as a PROXY within Playwright
    # This gives us a Real Saudi Residential IP
    proxy = {
        "server": "http://api.scraperant.com:8080",
        "username": API_KEY,
        "password": ""
    }

    page = browser.new_page(proxy=proxy)
    stealth_sync(page) # Hides the 'Bot' fingerprint
    
    try:
        page.goto(urls[platform], wait_until="networkidle", timeout=60000)
        time.sleep(5) # Let dynamic prices load
        
        if platform == "noon":
            price_element = page.query_selector(".amount")
            return price_element.inner_text() if price_element else "N/A"
        
        # Logic for Hungerstation/Ninja/Keeta
        # We look for SAR text on the page
        content = page.content()
        if "SAR" in content or "SR" in content:
            # Simple logic to find price numbers near SAR
            return "Found" # You can refine this to pull exact text
        return "Not Found"
    except:
        return "Blocked"
    finally:
        page.close()

# --- RUNNING FOR 1 TEST ITEM ---
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        test_item = {"code": "PPMP500TP1", "barcode": "05056141850689"}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        print(f"Testing {test_item['code']}...")
        result = {
            "Date": timestamp,
            "Product Code": test_item['code'],
            "Noon": get_price_stealth(browser, test_item['barcode'], "noon"),
            "Hungerstation": get_price_stealth(browser, test_item['barcode'], "hungerstation")
        }
        
        print(result)
        pd.DataFrame([result]).to_csv("ksa_master_report.csv", index=False)
        browser.close()

if __name__ == "__main__":
    run()
