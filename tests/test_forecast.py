import pandas as pd

from bovintel.models.export_forecast import backtest_and_forecast


def test_forecast_outputs():
    periods = pd.date_range("2020-01-01", periods=36, freq="MS")
    monthly = pd.DataFrame({"period": periods, "net_weight_kg": range(100, 136)})
    metrics, forecast = backtest_and_forecast(monthly, horizon=6)
    assert {"model", "mae", "rmse", "mape"}.issubset(metrics.columns)
    assert len(forecast) == 6
