from __future__ import annotations

import pandas as pd

from bovintel.analysis.indicators import safe_divide

REQUIRED = {
    "year",
    "month",
    "destination_country",
    "ncm_code",
    "export_value_usd_fob",
    "net_weight_kg",
}


def clean_exports(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip().lower() for c in df.columns}).copy()
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"exports_monthly sem colunas obrigatorias: {sorted(missing)}")
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["period"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    df["ncm_code"] = df["ncm_code"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(4)
    df["export_value_usd_fob"] = pd.to_numeric(df["export_value_usd_fob"], errors="coerce")
    df["net_weight_kg"] = pd.to_numeric(df["net_weight_kg"], errors="coerce")
    df["avg_export_price_usd_per_kg"] = safe_divide(df["export_value_usd_fob"], df["net_weight_kg"])
    return df[list(REQUIRED) + ["period", "avg_export_price_usd_per_kg"]]
