import pandas as pd
import pytest

from bovintel.analysis.indicators import cagr, percent_change, safe_divide


def test_growth_and_safe_division():
    assert percent_change(pd.Series([100, 110])).iloc[1] == pytest.approx(10)
    assert round(cagr(100, 121, 2), 2) == 10
    assert pd.isna(safe_divide(pd.Series([1]), pd.Series([0])).iloc[0])
