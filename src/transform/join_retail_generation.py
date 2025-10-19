from pathlib import Path
import pandas as pd

processed = Path("data") / "processed"

# --- Load both datasets ---
retail = pd.read_csv(processed / "retail_ga_kpis.csv", parse_dates=["period"])
generation = pd.read_csv(processed / "generation_ga_fuel_monthly.csv", parse_dates=["period"])

# --- Pivot fuel mix so each fuel is its own column ---
fuel_pivot = generation.pivot_table(
    index="period",
    columns="fuelTypeDescription",
    values="fuel_share",
    aggfunc="first"  # each period/fuel unique
)

# Flatten column index
fuel_pivot.columns = [f"{c}_share" for c in fuel_pivot.columns]
fuel_pivot = fuel_pivot.reset_index()

# --- Merge with retail KPIs on 'period' ---
merged = pd.merge(retail, fuel_pivot, on="period", how="left")

# --- Save ---
out = processed / "retail_generation_merged.csv"
merged.to_csv(out, index=False)
print(f"Saved merged dataset to: {out}")
print(merged.head(3))
