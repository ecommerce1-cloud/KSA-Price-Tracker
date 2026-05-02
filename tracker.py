import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

# --- CONFIGURATION ---
API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_platform_price(barcode, platform):
    urls = {
        "noon": f"https://www.noon.com/saudi-en/search/?q={barcode}",
        "hungerstation": f"https://hungerstation.com/sa-en/search?q={barcode}",
        "ninja": f"https://aswaqninja.com/search?q={barcode}",
        "keeta": f"https://www.keeta.com/sa/search?q={barcode}"
    }
    
    target_url = urls.get(platform)
    
    # --- ENHANCED SCRAPING SETTINGS ---
    # proxy_type=residential: Essential for KSA apps
    # proxy_country=sa: Forces the IP to be inside Saudi Arabia
    # browser=true: Necessary for Ninja/Keeta/HungerStation
    api_url = (
        f"https://api.scraperant.com/v2/general?"
        f"url={target_url}&x-api-key={API_KEY}&browser=true"
        f"&proxy_type=residential&proxy_country=sa"
    )
    
    try:
        # We increase the Python timeout to 120 seconds
        response = requests.get(api_url, timeout=120)
        
        if response.status_code == 403:
            return "Key Error/Limit"
        if response.status_code != 200:
            return f"Error {response.status_code}"

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Noon Logic
        if platform == "noon":
            price = soup.find("span", class_="amount")
            return price.text.strip() if price else "N/A"
        
        # General Price Search for delivery apps
        # (Looking for numbers followed by SAR or SR)
        price_tags = soup.find_all(text=lambda t: "SAR" in t or "SR" in t or "ريال" in t)
        if price_tags:
            return price_tags[0].strip().replace('SAR', '').replace('SR', '').strip()
            
        return "Not Found"
    except requests.exceptions.Timeout:
        return "Script Timeout"
    except Exception:
        return "Failed"

# --- YOUR PRODUCT DATA ---
input_data = [
    {"code": "PPMP500TP1", "barcode": "05056141850689"},
    {"code": "PPAF200HPX2", "barcode": "5056141850764"},
    {"code": "PPGBR80110X3PKT", "barcode": "5056141850788"},
    {"code": "PPDBBX3", "barcode": "5056141850825"},
    {"code": "PPPC6X3", "barcode": "5056141850849"},
    {"code": "PPAPOT256", "barcode": "5056141851259"},
    {"code": "PPAPOT296", "barcode": "5056141851266"},
    {"code": "PPZLB1821TP", "barcode": "5056141852423"},
    {"code": "SNCFT200NP5", "barcode": "5056141852690"},
    {"code": "HSMGBR6595X60", "barcode": "5056141852751"},
    {"code": "PPAF3P75HP2PLUS1M11", "barcode": "5056141853093"},
    {"code": "HSMCG12PETDC", "barcode": "5056141853765"},
    {"code": "PHDC4SC", "barcode": "5056141853901"},
    {"code": "PHDC6P5SC2", "barcode": "5056141853918"},
    {"code": "DWPC8RAM", "barcode": "5056141853925"},
    {"code": "SF20RAM", "barcode": "5056141854120"},
    {"code": "PPMRJT1305P1", "barcode": "5056141854700"},
    {"code": "PPMRJT1704P1", "barcode": "5056141854724"},
    {"code": "APFL500", "barcode": "5056141855110"},
    {"code": "APFL200", "barcode": "5056141855134"},
    {"code": "HSMAFPBR164CM", "barcode": "5056141855219"},
    {"code": "HSMAFPBR204CM", "barcode": "5056141855226"},
    {"code": "HSMAFPBS16164CM", "barcode": "5056141855233"},
    {"code": "PPSNCMPT150X4PKT", "barcode": "5056141855516"},
    {"code": "PPAF25SQFT2PLUS1M11", "barcode": "5056141856087"},
    {"code": "HSMPC9HWRPS", "barcode": "5056141856230"},
    {"code": "PPSOFRAOFFERTP", "barcode": "5056141857282"},
    {"code": "PPMC500X5", "barcode": "5056141857336"},
    {"code": "PPAF30250HPE", "barcode": "5056141857664"},
    {"code": "PPHDMC1000500TP", "barcode": "5056141857725"}
]

results = []
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

for item in input_data:
    print(f"Fetching {item['code']}...")
    results.append({
        "Date": timestamp,
        "Product Code": item['code'],
        "Barcode": item['barcode'],
        "Ninja RSP": get_platform_price(item['barcode'], "ninja"),
        "Noon RSP": get_platform_price(item['barcode'], "noon"),
        "Keeta RSP": get_platform_price(item['barcode'], "keeta"),
        "Hungerstation RSP": get_platform_price(item['barcode'], "hungerstation")
    })
    time.sleep(2) # Politeness delay

df = pd.DataFrame(results)
file_exists = os.path.isfile("ksa_master_report.csv")
df.to_csv("ksa_master_report.csv", mode='a', index=False, header=not file_exists)
