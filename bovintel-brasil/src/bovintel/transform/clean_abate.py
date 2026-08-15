from __future__ import annotations

import pandas as pd

from bovintel.analysis.indicators import safe_divide
from bovintel.transform.clean_ppm import UF_NAMES

REQUIRED = {"year", "quarter", "state_code", "state_name", "slaughtered_heads", "carcass_weight_kg"}


def clean_slaughter(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip().lower() for c in df.columns}).copy()
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"slaughter_quarterly sem colunas obrigatorias: {sorted(missing)}")
    df["year"] = df["year"].astype(int)
    df["quarter"] = df["quarter"].astype(int)
    df["state_code"] = df["state_code"].astype(str).str.zfill(2)
    df["state_name"] = df["state_code"].map(UF_NAMES).fillna(df["state_name"])
    quarter_period = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
    df["period"] = pd.PeriodIndex(quarter_period, freq="Q").to_timestamp()
    df["slaughtered_heads"] = pd.to_numeric(df["slaughtered_heads"], errors="coerce")
    df["carcass_weight_kg"] = pd.to_numeric(df["carcass_weight_kg"], errors="coerce")
    df["avg_carcass_weight_kg_per_head"] = safe_divide(
        df["carcass_weight_kg"], df["slaughtered_heads"]
    )
    return df[
        [
            "year",
            "quarter",
            "period",
            "state_code",
            "state_name",
            "slaughtered_heads",
            "carcass_weight_kg",
            "avg_carcass_weight_kg_per_head",
        ]
    ]
