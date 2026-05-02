import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_noon_price_direct(barcode):
    # Search URL - Noon often redirects this to the product page
    target_url = f"https://www.noon.com/saudi-en/search/?q={barcode}"
    
    # We use 'render_js=true' to ensure the page fully loads
    api_url = (
        f"https://api.scraperant.com/v2/general?"
        f"url={target_url}&x-api-key={API_KEY}"
        f"&browser=true&proxy_type=residential&proxy_country=sa"
    )

    try:
        response = requests.get(api_url, timeout=60)
        if response.status_code != 200:
            return f"Error {response.status_code}"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Noon Price Selectors (Trying multiple common ones)
        price = None
        
        # 1. Standard search result price
        price_tag = soup.select_one(".amount")
        # 2. Product page price (if redirected)
        if not price_tag:
            price_tag = soup.select_one('span[class*="priceNow"]')
        
        if price_tag:
            return price_tag.text.strip()
            
        return "Not Found"
    except:
        return "Timeout"

def run():
    # Let's just do 5 items to keep the credits low and speed up
    test_items = [
        {"code": "PPMP500TP1", "barcode": "05056141850689"},
        {"code": "PPAF200HPX2", "barcode": "5056141850764"},
        {"code": "PPGBR80110X3PKT", "barcode": "5056141850788"},
        {"code": "PPDBBX3", "barcode": "5056141850825"},
        {"code": "PPPC6X3", "barcode": "5056141850849"}
    ]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    results = []

    for item in test_items:
        print(f"Checking {item['code']}...")
        price = get_noon_price_direct(item['barcode'])
        results.append({
            "Date": timestamp,
            "Product Code": item['code'],
            "Barcode": item['barcode'],
            "Noon RSP": price
        })
        time.sleep(10) # Polite delay

    df = pd.DataFrame(results)
    df.to_csv("ksa_master_report.csv", index=False)

if __name__ == "__main__":
    run()
