import requests
from src.utils.config import EIA_API_KEY
import json
from pathlib import Path
from datetime import datetime

url = (
    f"https://api.eia.gov/v2/electricity/facility-fuel/data"
    f"?api_key={EIA_API_KEY}"
    f"&frequency=monthly"
    f"&data[]=generation&data[]=gross-generation"
    f"&facets[state][]=GA"
    f"&start=2024-07&end=2025-07"   # <-- use the month you saw in your DF
    f"&sort[0][column]=period&sort[0][direction]=desc"
    f"&length=5000"
)

resp = requests.get(url, timeout=30)
payload = resp.json()

raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)

ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
fname = raw_dir / f"generation_ga_{ts}.json"

with fname.open('w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)

print(f"Saved raw payload to: {fname}")