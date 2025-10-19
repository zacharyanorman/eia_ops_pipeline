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

# Compute fuel mix share for the period (based on net generation)
total_by_period = fuel_monthly.groupby("period")["generation"].transform("sum")
fuel_monthly["fuel_share"] = fuel_monthly["generation"] / total_by_period

print(fuel_monthly.head(10))
