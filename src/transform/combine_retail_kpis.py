from pathlib import Path
import pandas as pd

processed_dir = Path("data") / "processed"
df_res = pd.read_csv(processed_dir / "retail_ga_RES_kpis.csv", parse_dates=["period"])
df_com = pd.read_csv(processed_dir / "retail_ga_COM_kpis.csv", parse_dates=["period"])

combined = pd.concat([df_res, df_com], ignore_index=True)
combined = combined.sort_values(["period", "sectorid"])

out_path = processed_dir / "retail_ga_kpis.csv"
combined.to_csv(out_path, index=False)
print(f"Saved combined KPIs to: {out_path}")
