from __future__ import annotations

import pandas as pd
from scipy import stats


def correlations(df: pd.DataFrame, x: str, y: str) -> pd.DataFrame:
    pairs = df[[x, y]].dropna()
    if len(pairs) < 3:
        return pd.DataFrame(
            [
                {"method": "pearson", "n": len(pairs), "correlation": None, "p_value": None},
                {"method": "spearman", "n": len(pairs), "correlation": None, "p_value": None},
            ]
        )
    pearson = stats.pearsonr(pairs[x], pairs[y])
    spearman = stats.spearmanr(pairs[x], pairs[y])
    return pd.DataFrame(
        [
            {
                "method": "pearson",
                "n": len(pairs),
                "correlation": pearson.statistic,
                "p_value": pearson.pvalue,
            },
            {
                "method": "spearman",
                "n": len(pairs),
                "correlation": spearman.statistic,
                "p_value": spearman.pvalue,
            },
        ]
    )
