from __future__ import annotations

import numpy as np
import pandas as pd


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.replace(0, np.nan))


def percent_change(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.pct_change(periods=periods) * 100


def cagr(start_value: float, end_value: float, periods: int) -> float:
    if periods <= 0 or start_value <= 0 or end_value < 0:
        return np.nan
    return ((end_value / start_value) ** (1 / periods) - 1) * 100


def add_share(
    df: pd.DataFrame, value_col: str, group_cols: list[str], share_col: str
) -> pd.DataFrame:
    out = df.copy()
    totals = out.groupby(group_cols, dropna=False)[value_col].transform("sum")
    out[share_col] = safe_divide(out[value_col], totals) * 100
    return out


def top_n(df: pd.DataFrame, value_col: str, n: int = 10) -> pd.DataFrame:
    return df.sort_values(value_col, ascending=False).head(n).reset_index(drop=True)
