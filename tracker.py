import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time
import random

API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_noon_price(barcode):
    url = f"https://www.noon.com/saudi-en/search/?q={barcode}"
    api_url = f"https://api.scraperant.com/v2/general?url={url}&x-api-key={API_KEY}&browser=true"
    try:
        res = requests.get(api_url, timeout=60)
        soup = BeautifulSoup(res.content, "html.parser")
        price = soup.find("span", class_="amount")
        return price.text.strip() if price else "N/A"
    except:
        return "Error"

def get_delivery_app_price(barcode, platform):
    # Instead of the app, we ask Google: "What is the price of [barcode] on [platform]?"
    # This is much harder for them to block.
    search_query = f"site:{platform}.com {barcode} price SAR"
    url = f"https://www.google.com/search?q={search_query}"
    api_url = f"https://api.scraperant.com/v2/general?url={url}&x-api-key={API_KEY}&browser=true"
    
    try:
        res = requests.get(api_url, timeout=60)
        soup = BeautifulSoup(res.content, "html.parser")
        # Look for SAR/SR in the search snippets
        snippet = soup.find(text=lambda t: "SAR" in t or "SR" in t)
        if snippet:
            return snippet.strip()
        return "Check App"
    except:
        return "Blocked"

# --- TEST WITH FIRST 3 ITEMS ---
input_data = [
    {"code": "PPMP500TP1", "barcode": "05056141850689"},
    {"code": "PPAF200HPX2", "barcode": "5056141850764"},
    {"code": "PPGBR80110X3PKT", "barcode": "5056141850788"}
]

results = []
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

for item in input_data:
    print(f"Tracking {item['code']}...")
    results.append({
        "Date": timestamp,
        "Product Code": item['code'],
        "Barcode": item['barcode'],
        "Noon RSP": get_noon_price(item['barcode']),
        "Ninja RSP": get_delivery_app_price(item['barcode'], "aswaqninja"),
        "Keeta RSP": get_delivery_app_price(item['barcode'], "keeta"),
        "Hungerstation RSP": get_delivery_app_price(item['barcode'], "hungerstation")
    })
    time.sleep(10)

df = pd.DataFrame(results)
df.to_csv("ksa_master_report.csv", mode='a', index=False, header=not os.path.exists("ksa_master_report.csv"))
