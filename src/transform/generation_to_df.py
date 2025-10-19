from pathlib import Path
import json
import pandas as pd

# 1) pick the newest saved raw file for this sector
raw_dir = Path("data") / "raw"
files = sorted(raw_dir.glob(f"generation_ga_*.json"))
latest = files[-1]  # newest timestamped file

# 2) read JSON payload and extract the 'data' list
with latest.open("r", encoding="utf-8") as f:
    payload = json.load(f)

rows = payload.get("response", {}).get("data", [])

# 3) make a DataFrame and take a quick look
df = pd.DataFrame(rows)

# Convert period to datetime
df["period"] = pd.to_datetime(df["period"], format="%Y-%m")

# Convert numeric columns
for col in ["generation", "gross-generation"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print(df.dtypes)
print(df.head(3))

# Summarize by fuel type (monthly)
fuel_monthly = (
    df.groupby(["period", "fuelTypeDescription"], as_index=False)[["generation", "gross-generation"]]
      .sum()
      .sort_values(["period", "generation"], ascending=[True, False])
)

# 1) exclude the summary row and any negative net generation (e.g., pumped storage can be negative)
clean = fuel_monthly[ fuel_monthly["fuelTypeDescription"].str.lower() != "total" ].copy()
clean = clean[ clean["generation"] > 0 ].copy()

# 2) recompute the denominator (sum of positive net generation only)
denom = clean.groupby("period")["generation"].transform("sum")

# 3) new fuel shares
clean["fuel_share"] = clean["generation"] / denom

print(clean[["period","fuelTypeDescription","generation","fuel_share"]].head(12))

# 4) save the cleaned version instead of the raw one
from pathlib import Path
processed_dir = Path("data") / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)
out_path = processed_dir / "generation_ga_fuel_monthly.csv"
clean.to_csv(out_path, index=False)
print(f"Saved cleaned fuel summary to: {out_path}")