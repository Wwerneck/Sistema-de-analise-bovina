from __future__ import annotations

import numpy as np
import pandas as pd


def shares_percent(values: pd.Series) -> pd.Series:
    total = values.sum(skipna=True)
    if total <= 0:
        return pd.Series(np.nan, index=values.index, dtype="float64")
    return values / total * 100


def concentration_ratio(values: pd.Series, n: int) -> float:
    shares = shares_percent(values.fillna(0)).sort_values(ascending=False)
    return float(shares.head(n).sum())


def hhi(values: pd.Series) -> float:
    shares = shares_percent(values.fillna(0))
    return float((shares**2).sum())


def pareto_80_count(values: pd.Series) -> int:
    shares = shares_percent(values.fillna(0)).sort_values(ascending=False)
    if shares.isna().all():
        return 0
    return int((shares.cumsum() < 80).sum() + 1)


def classify_hhi(hhi_value: float) -> str:
    if np.isnan(hhi_value):
        return "indefinido"
    if hhi_value < 1500:
        return "baixa concentracao"
    if hhi_value < 2500:
        return "concentracao moderada"
    return "alta concentracao"


def concentration_summary(values: pd.Series) -> dict[str, float | int | str]:
    score = hhi(values)
    return {
        "cr3_percent": concentration_ratio(values, 3),
        "cr5_percent": concentration_ratio(values, 5),
        "hhi": score,
        "pareto_80_count": pareto_80_count(values),
        "classification": classify_hhi(score),
    }
