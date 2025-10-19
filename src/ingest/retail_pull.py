import requests
from src.utils.config import EIA_API_KEY
import json
from pathlib import Path
from datetime import datetime

SECTOR = "COM"

url = (
    f"https://api.eia.gov/v2/electricity/retail-sales/data"
    f"?api_key={EIA_API_KEY}"
    f"&frequency=monthly"
    f"&data[]=price&data[]=revenue&data[]=sales&data[]=customers"
    f"&facets[stateid][]=GA"
    f"&facets[sectorid][]={SECTOR}"
    f"&sort[0][column]=period&sort[0][direction]=desc"
    f"&length=1"
)

resp = requests.get(url, timeout=30)
payload = resp.json()

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
fname = raw_dir / f"retail_ga_{SECTOR}_{ts}.json"

with fname.open('w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"Saved raw payload to: {fname}")