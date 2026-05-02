import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

# --- CONFIGURATION ---
API_KEY = '16c053b74712483dbe984acc98d8814f'

def get_platform_price(barcode, platform):
    # Constructing search URLs for KSA platforms
    urls = {
        "noon": f"https://www.noon.com/saudi-en/search/?q={barcode}",
        "hungerstation": f"https://hungerstation.com/sa-en/search?q={barcode}",
        "ninja": f"https://aswaqninja.com/search?q={barcode}",
        "keeta": f"https://www.keeta.com/sa/search?q={barcode}"
    }
    
    target_url = urls.get(platform)
    # Using ScraperAnt to bypass KSA firewalls and mimic local location
    api_url = f"https://api.scraperant.com/v2/general?url={target_url}&x-api-key={API_KEY}&browser=true"
    
    try:
        response = requests.get(api_url, timeout=60)
        soup = BeautifulSoup(response.content, "html.parser")
        
        if platform == "noon":
            price = soup.find("span", class_="amount")
            return price.text.strip() if price else "N/A"
        else:
            # Generic selector for delivery apps
            price = soup.find(text=lambda t: "SAR" in t or "SR" in t)
            return price.strip().replace('SAR', '').strip() if price else "N/A"
    except:
        return "Timeout"

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
