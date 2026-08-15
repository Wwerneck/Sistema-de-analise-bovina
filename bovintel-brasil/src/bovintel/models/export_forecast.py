from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


def can_fit_holt_winters(series: pd.Series) -> bool:
    return len(series) >= 36 and not series.isna().any() and (series > 0).all()


def metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    actual, predicted = actual.align(predicted, join="inner")
    valid = pd.concat([actual, predicted], axis=1).dropna()
    actual = valid.iloc[:, 0]
    predicted = valid.iloc[:, 1]
    err = actual - predicted
    nonzero = actual.replace(0, np.nan)
    return {
        "mae": float(err.abs().mean()),
        "rmse": float(np.sqrt((err**2).mean())),
        "mape": float((err.abs() / nonzero).mean() * 100),
    }


def seasonal_naive(series: pd.Series, horizon: int) -> pd.Series:
    series = series.dropna()
    if len(series) < 12:
        return pd.Series([series.iloc[-1]] * horizon)
    reps = int(np.ceil(horizon / 12))
    vals = np.tile(series.iloc[-12:].to_numpy(), reps)[:horizon]
    return pd.Series(vals)


def backtest_and_forecast(
    monthly: pd.DataFrame, horizon: int = 6
) -> tuple[pd.DataFrame, pd.DataFrame]:
    series = monthly.sort_values("period").set_index("period")["net_weight_kg"].asfreq("MS")
    series = series.astype(float)
    test_size = min(12, max(1, len(series) - 24))
    if len(series) < 25:
        raise ValueError("Serie de exportacao precisa ter pelo menos 25 meses para backtest.")
    train, test = series.iloc[:-test_size], series.iloc[-test_size:]
    candidates: list[tuple[str, pd.Series]] = [
        ("baseline_sazonal_ingenuo", seasonal_naive(train, len(test)).set_axis(test.index))
    ]
    if can_fit_holt_winters(train):
        try:
            model = ExponentialSmoothing(
                train, trend="add", seasonal="add", seasonal_periods=12
            ).fit()
            candidates.append(("holt_winters", model.forecast(len(test))))
        except ValueError:
            pass
    scored = []
    for name, pred in candidates:
        scored.append({"model": name, **metrics(test, pred)})
    metrics_df = pd.DataFrame(scored).sort_values("mae").reset_index(drop=True)
    best = metrics_df.loc[0, "model"]
    if best == "holt_winters" and can_fit_holt_winters(series):
        final_model = ExponentialSmoothing(
            series, trend="add", seasonal="add", seasonal_periods=12
        ).fit()
        forecast = final_model.forecast(horizon)
    else:
        idx = pd.date_range(
            series.index.max() + pd.offsets.MonthBegin(), periods=horizon, freq="MS"
        )
        forecast = seasonal_naive(series, horizon).set_axis(idx)
    forecast_df = forecast.rename("forecast_net_weight_kg").reset_index()
    forecast_df = forecast_df.rename(columns={forecast_df.columns[0]: "period"})
    forecast_df["model"] = best
    return metrics_df, forecast_df
