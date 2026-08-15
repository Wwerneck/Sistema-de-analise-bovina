import pandas as pd

from bovintel.analysis.concentration import concentration_ratio, hhi, pareto_80_count


def test_concentration_metrics():
    values = pd.Series([40, 30, 20, 10])
    assert concentration_ratio(values, 3) == 90
    assert concentration_ratio(values, 5) == 100
    assert hhi(values) == 3000
    assert pareto_80_count(values) == 3
