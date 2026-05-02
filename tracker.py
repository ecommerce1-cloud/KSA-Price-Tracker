import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time

# YOUR ACTUAL KEY HERE
API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_noon_price(browser, barcode):
    url = f"https://www.noon.com/saudi-en/search/?q={barcode}"
    
    proxy = {
        "server": "http://api.scraperant.com:8080",
        "username": API_KEY,
        "password": ""
    }

    context = browser.new_context(proxy=proxy)
    page = context.new_page()
    
    try:
        # Noon loads fast, but we give it 30s
        page.goto(url, wait_until="load", timeout=30000)
        time.sleep(5) 
        
        price_element = page.query_selector(".amount")
        if price_element:
            return price_element.inner_text().strip()
        return "N/A"
    except Exception as e:
        print(f"Noon Error: {str(e)}")
        return "Timeout"
    finally:
        context.close()

def run():
    with sync_playwright() as p:
        # Launching with specific flags to avoid GitHub Action crashes
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        
        # Testing just the first 2 barcodes to ensure it works
        test_items = [
            {"code": "PPMP500TP1", "barcode": "05056141850689"},
            {"code": "PPAF200HPX2", "barcode": "5056141850764"}
        ]
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        final_data = []

        for item in test_items:
            print(f"Checking {item['code']}...")
            price = get_noon_price(browser, item['barcode'])
            final_data.append({
                "Date": timestamp,
                "Product Code": item['code'],
                "Barcode": item['barcode'],
                "Noon RSP": price
            })
            time.sleep(2)

        df = pd.DataFrame(final_data)
        df.to_csv("ksa_master_report.csv", index=False)
        browser.close()
        print("Success!")

if __name__ == "__main__":
    run()
