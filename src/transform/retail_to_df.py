from pathlib import Path
import json
import pandas as pd

SECTOR = "RES"  # change to "COM" to load the commercial file

# 1) pick the newest saved raw file for this sector
raw_dir = Path("data") / "raw"
files = sorted(raw_dir.glob(f"retail_ga_{SECTOR}_*.json"))
latest = files[-1]  # newest timestamped file

print("Loading:", latest)

# 2) read JSON payload and extract the 'data' list
with latest.open("r", encoding="utf-8") as f:
    payload = json.load(f)

rows = payload.get("response", {}).get("data", [])

# 3) make a DataFrame and take a quick look
df = pd.DataFrame(rows)

# Convert period to a datetime (monthly)
df["period"] = pd.to_datetime(df["period"], format="%Y-%m")

# Convert numeric fields from strings to floats
for col in ["price", "revenue", "sales", "customers"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Unit-safe conversions (based on the units columns you saw) ---
sales = df["sales"].astype(float).copy()

units_sales = df["sales-units"].iloc[0].lower()
if units_sales.startswith("thousand"):
    sales = sales * 1_000.0
elif units_sales.startswith("million"):
    sales = sales * 1_000_000.0
elif units_sales.startswith("billion"):
    sales = sales * 1_000_000_000.0
# else: assume the value is already in kWh

rev = df["revenue"].astype(float).copy()

units_rev = df["revenue-units"].iloc[0].lower()
if units_rev.startswith("thousand"):
    rev = rev * 1_000.0
elif units_rev.startswith("million"):
    rev = rev * 1_000_000.0
elif units_rev.startswith("billion"):
    rev = rev * 1_000_000_000.0
# else: assume already dollars

cust = df["customers"].astype(float).copy()
price_cents_per_kwh = df["price"].astype(float).copy()

# price is already "cents per kilowatt-hour" per your printout
price_dollars_per_kwh = price_cents_per_kwh / 100.0

# --- KPIs ---
# 1) revenue per customer (dollars/customer)
kpi_revenue_per_customer = (rev / cust).rename("rev_per_customer")

# 2) kWh per customer
kpi_kwh_per_customer = (sales / cust).rename("kwh_per_customer")

# 3) realized revenue per kWh in dollars/kWh (should roughly match price_dollars_per_kwh)
kpi_revenue_per_kwh = (rev / sales).rename("rev_per_kwh")

kpis = pd.concat(
    [df["period"], df["stateid"], df["sectorid"],
     kpi_revenue_per_customer, kpi_kwh_per_customer, kpi_revenue_per_kwh,
     price_dollars_per_kwh.rename("listed_price_dollars_per_kwh")],
    axis=1
)

print(kpis.head(3))

processed_dir = Path("data") / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

out_path = processed_dir / f"retail_ga_{SECTOR}_kpis.csv"
kpis.to_csv(out_path, index=False)
print(f"Saved KPIs to: {out_path}")