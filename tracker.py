import pandas as pd
import requests
from datetime import datetime
import os
import time

# YOUR ACTUAL KEY HERE
API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_noon_price_direct(barcode):
    # This URL targets the product search on Noon KSA
    target_url = f"https://www.noon.com/saudi-en/search/?q={barcode}"
    
    # We ask ScrapingAnt to use a Saudi Residential Proxy and a Real Browser
    # 'wait_for_selector' ensures the price actually loads before returning the data
    api_url = (
        f"https://api.scraperant.com/v2/general?"
        f"url={target_url}&x-api-key={API_KEY}&browser=true"
        f"&proxy_type=residential&proxy_country=sa"
        f"&wait_for_selector=.amount"
    )

    try:
        # We give the API 90 seconds to find the price
        response = requests.get(api_url, timeout=100)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            price_element = soup.select_one(".amount")
            if price_element:
                return price_element.text.strip()
            return "Not Found"
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return "Timeout"

def run():
    # Testing just the first 2 barcodes to keep it fast
    test_items = [
        {"code": "PPMP500TP1", "barcode": "05056141850689"},
        {"code": "PPAF200HPX2", "barcode": "5056141850764"}
    ]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    final_data = []

    for item in test_items:
        print(f"Checking {item['code']}...")
        # We add a longer delay between products to be very stealthy
        price = get_noon_price_direct(item['barcode'])
        final_data.append({
            "Date": timestamp,
            "Product Code": item['code'],
            "Barcode": item['barcode'],
            "Noon RSP": price
        })
        time.sleep(15)

    df = pd.DataFrame(final_data)
    df.to_csv("ksa_master_report.csv", index=False)
    print("Process Finished.")

if __name__ == "__main__":
    run()
