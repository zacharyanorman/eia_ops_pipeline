import requests
from src.utils.config import EIA_API_KEY
import json
from pathlib import Path
import datetime

def last_full_month():
    today = datetime.date.today()
    y, m = today.year, today.month
    if m == 1:
        return y - 1, 12
    return y, m - 1

def add_months(y: int, m: int, delta: int):
    total = y * 12 + (m - 1) + delta  # zero-based month math
    ny, nm0 = divmod(total, 12)
    return ny, nm0 + 1  # back to 1-based month

end_y, end_m = last_full_month()       # last complete month
start_y, start_m = add_months(end_y, end_m, -17)  # 18 months inclusive

START = f"{start_y:04d}-{start_m:02d}"
END   = f"{end_y:04d}-{end_m:02d}"
print("Retail window:", START, "to", END)

SECTOR = "COM"

url = (
    f"https://api.eia.gov/v2/electricity/retail-sales/data"
    f"?api_key={EIA_API_KEY}"
    f"&frequency=monthly"
    f"&data[]=price&data[]=revenue&data[]=sales&data[]=customers"
    f"&facets[stateid][]=GA"
    f"&facets[sectorid][]={SECTOR}"
    f"&start={START}&end={END}"
    f"&sort[0][column]=period&sort[0][direction]=desc"
    f"&length=5000"
)

resp = requests.get(url, timeout=30)
payload = resp.json()

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

ts = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
fname = raw_dir / f"retail_ga_{SECTOR}_{ts}.json"

with fname.open('w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"Saved raw payload to: {fname}")