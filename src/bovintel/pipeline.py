from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

from bovintel.analysis.concentration import concentration_summary
from bovintel.analysis.statistics import correlations
from bovintel.config import ensure_dirs, settings
from bovintel.extract.comexstat import locate_comex_csv
from bovintel.models.export_forecast import backtest_and_forecast
from bovintel.transform.clean_abate import clean_slaughter
from bovintel.transform.clean_comex import clean_exports
from bovintel.transform.clean_ppm import clean_herd
from bovintel.visualization.charts import save_figures


def _path(name: str) -> Path:
    return Path(settings()["paths"][name])


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _raw_symbol_counts(raw_path: Path) -> dict[str, int]:
    if not raw_path.exists():
        return {"raw_zero_symbols": 0, "raw_suppressed_symbols": 0, "raw_unavailable_symbols": 0}
    raw = pd.read_csv(raw_path, dtype=str, keep_default_na=False)
    values = raw.astype(str)
    return {
        "raw_zero_symbols": int(values.isin(["-"]).sum().sum()),
        "raw_suppressed_symbols": int(values.isin(["X"]).sum().sum()),
        "raw_unavailable_symbols": int(values.isin(["..."]).sum().sum()),
    }


def data_quality_profile(table: str, df: pd.DataFrame, keys: list[str]) -> dict[str, int | str]:
    numeric = df.select_dtypes("number")
    raw_files = {
        "herd_annual": "herd_annual.csv",
        "slaughter_quarterly": "slaughter_quarterly.csv",
        "exports_monthly": "comex_exports.csv",
    }
    profile = {
        "table": table,
        "rows": len(df),
        "duplicate_keys": int(df.duplicated(keys).sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "zero_numeric_cells": int((numeric == 0).sum().sum()),
    }
    profile.update(_raw_symbol_counts(_path("raw") / raw_files[table]))
    return profile


def _pct_change(current: float, previous: float) -> float | None:
    if previous in (0, None) or pd.isna(previous):
        return None
    return (current / previous - 1) * 100


def _dashboard_indicators(
    herd_year: pd.DataFrame,
    herd_state_year: pd.DataFrame,
    slaughter_quarter: pd.DataFrame,
    exports_month: pd.DataFrame,
    destination_year: pd.DataFrame,
    concentration: dict,
) -> dict:
    latest_herd = herd_year.sort_values("year").iloc[-1]
    previous_herd = herd_year.sort_values("year").iloc[-2]
    latest_herd_year = int(latest_herd["year"])
    latest_uf = (
        herd_state_year[herd_state_year["year"] == latest_herd_year]
        .sort_values("bovine_herd_heads", ascending=False)
        .iloc[0]
    )
    slaughter_sorted = slaughter_quarter.sort_values("period")
    latest_slaughter = slaughter_sorted.iloc[-1]
    previous_slaughter = slaughter_sorted.iloc[-2]
    exports_sorted = exports_month.sort_values("period")
    latest_exports = exports_sorted.iloc[-1]
    previous_exports = exports_sorted.iloc[-2]
    latest_export_year = int(str(latest_exports["period"])[:4])
    latest_dest = (
        destination_year[destination_year["year"] == latest_export_year]
        .sort_values("net_weight_kg", ascending=False)
        .iloc[0]
    )
    export_trend_3m = (
        exports_sorted["net_weight_kg"].tail(3).mean()
        / exports_sorted["net_weight_kg"].tail(6).head(3).mean()
        - 1
    ) * 100
    return {
        "latest_herd_year": latest_herd_year,
        "herd_heads": float(latest_herd["bovine_herd_heads"]),
        "herd_yoy_percent": _pct_change(
            latest_herd["bovine_herd_heads"], previous_herd["bovine_herd_heads"]
        ),
        "top_herd_state": latest_uf["state_name"],
        "top_herd_state_share_percent": float(
            latest_uf["bovine_herd_heads"] / latest_herd["bovine_herd_heads"] * 100
        ),
        "latest_slaughter_period": str(latest_slaughter["period"])[:10],
        "slaughtered_heads": float(latest_slaughter["slaughtered_heads"]),
        "slaughter_qoq_percent": _pct_change(
            latest_slaughter["slaughtered_heads"], previous_slaughter["slaughtered_heads"]
        ),
        "avg_carcass_weight_kg_per_head": float(
            latest_slaughter["avg_carcass_weight_kg_per_head"]
        ),
        "latest_export_period": str(latest_exports["period"])[:10],
        "export_value_usd_fob": float(latest_exports["export_value_usd_fob"]),
        "net_weight_kg": float(latest_exports["net_weight_kg"]),
        "export_volume_mom_percent": _pct_change(
            latest_exports["net_weight_kg"], previous_exports["net_weight_kg"]
        ),
        "export_trend_3m_vs_previous_3m_percent": float(export_trend_3m),
        "top_destination": latest_dest["destination_country"],
        "top_destination_share_percent": float(
            latest_dest["net_weight_kg"]
            / destination_year[destination_year["year"] == latest_export_year][
                "net_weight_kg"
            ].sum()
            * 100
        ),
        "destination_concentration": concentration["classification"],
    }


def _quarterly_correlation(
    slaughter_quarter: pd.DataFrame, exports_month: pd.DataFrame
) -> list[dict]:
    slaughter = slaughter_quarter.copy()
    slaughter["quarter_period"] = pd.to_datetime(slaughter["period"]).dt.to_period("Q")
    exports = exports_month.copy()
    exports["quarter_period"] = pd.to_datetime(exports["period"]).dt.to_period("Q")
    exports_q = exports.groupby("quarter_period", as_index=False)["net_weight_kg"].sum()
    merged = slaughter[["quarter_period", "slaughtered_heads"]].merge(
        exports_q, on="quarter_period", how="inner"
    )
    return correlations(merged, "slaughtered_heads", "net_weight_kg").to_dict("records")


def extract() -> None:
    ensure_dirs()
    raise RuntimeError(
        "Extracao automatica requer confirmar filtros SIDRA/Comex no ambiente. "
        "Use CSVs oficiais em data/raw/: herd_annual.csv, slaughter_quarterly.csv "
        "e comex_exports.csv."
    )


def transform() -> None:
    ensure_dirs()
    raw, processed = _path("raw"), _path("processed")
    herd = clean_herd(pd.read_csv(raw / "herd_annual.csv"))
    slaughter = clean_slaughter(pd.read_csv(raw / "slaughter_quarterly.csv"))
    exports = clean_exports(pd.read_csv(locate_comex_csv(raw)))
    herd.to_parquet(processed / "herd_annual.parquet", index=False)
    slaughter.to_parquet(processed / "slaughter_quarterly.parquet", index=False)
    exports.to_parquet(processed / "exports_monthly.parquet", index=False)


def validate() -> None:
    processed, tables = _path("processed"), _path("tables")
    tables.mkdir(parents=True, exist_ok=True)
    reports = []
    specs = {
        "herd_annual": ["year", "municipality_code"],
        "slaughter_quarterly": ["period", "state_code"],
        "exports_monthly": ["period", "destination_country", "ncm_code"],
    }
    for table, keys in specs.items():
        df = pd.read_parquet(processed / f"{table}.parquet")
        reports.append(data_quality_profile(table, df, keys))
        if df.duplicated(keys).any():
            raise ValueError(f"Chaves duplicadas em {table}: {keys}")
        numeric = df.select_dtypes("number")
        if (numeric < 0).any().any():
            raise ValueError(f"Valores negativos encontrados em {table}")
    pd.DataFrame(reports).to_csv(tables / "data_quality_report.csv", index=False)


def analyze() -> None:
    processed, tables = _path("processed"), _path("tables")
    herd = pd.read_parquet(processed / "herd_annual.parquet")
    exports = pd.read_parquet(processed / "exports_monthly.parquet")
    save_figures(herd, exports, _path("figures"))
    herd_state = herd.groupby(["year", "state_code", "state_name"], as_index=False)[
        "bovine_herd_heads"
    ].sum()
    herd_state.to_csv(tables / "herd_by_state_year.csv", index=False)
    latest = exports["period"].max()
    dest = (
        exports[exports["period"] == latest].groupby("destination_country")["net_weight_kg"].sum()
    )
    pd.DataFrame([concentration_summary(dest)]).to_csv(
        tables / "exports_concentration_latest.csv", index=False
    )


def forecast() -> None:
    exports = pd.read_parquet(_path("processed") / "exports_monthly.parquet")
    monthly = exports.groupby("period", as_index=False)["net_weight_kg"].sum()
    metrics, fcst = backtest_and_forecast(monthly, settings()["forecast"]["horizon_months"])
    metrics.to_csv(_path("models") / "forecast_metrics.csv", index=False)
    fcst.to_csv(_path("models") / "forecast.csv", index=False)


def dashboard() -> None:
    out = _path("dashboard_data")
    out.mkdir(parents=True, exist_ok=True)
    processed = _path("processed")
    herd = pd.read_parquet(processed / "herd_annual.parquet")
    slaughter = pd.read_parquet(processed / "slaughter_quarterly.parquet")
    exports = pd.read_parquet(processed / "exports_monthly.parquet")
    latest_exports = exports[exports["period"] == exports["period"].max()]
    quality_file = _path("tables") / "data_quality_report.csv"
    concentration = concentration_summary(
        latest_exports.groupby("destination_country")["net_weight_kg"].sum()
    )
    herd_year = herd.groupby("year", as_index=False)["bovine_herd_heads"].sum()
    herd_state_year = herd.groupby(
        ["year", "state_code", "state_name"], as_index=False
    )["bovine_herd_heads"].sum()
    slaughter_year = slaughter.groupby("year", as_index=False)[
        ["slaughtered_heads", "carcass_weight_kg"]
    ].sum()
    slaughter_year["avg_carcass_weight_kg_per_head"] = (
        slaughter_year["carcass_weight_kg"] / slaughter_year["slaughtered_heads"]
    )
    slaughter_quarter = slaughter.groupby("period", as_index=False)[
        ["slaughtered_heads", "carcass_weight_kg"]
    ].sum()
    slaughter_quarter["avg_carcass_weight_kg_per_head"] = (
        slaughter_quarter["carcass_weight_kg"] / slaughter_quarter["slaughtered_heads"]
    )
    exports_year = exports.groupby("year", as_index=False)[
        ["export_value_usd_fob", "net_weight_kg"]
    ].sum()
    exports_month = exports.groupby("period", as_index=False)[
        ["export_value_usd_fob", "net_weight_kg"]
    ].sum()
    destination_year = exports.groupby(
        ["year", "destination_country"], as_index=False
    )[["export_value_usd_fob", "net_weight_kg"]].sum()
    indicators = _dashboard_indicators(
        herd_year,
        herd_state_year,
        slaughter_quarter,
        exports_month,
        destination_year,
        concentration,
    )
    correlation = _quarterly_correlation(slaughter_quarter, exports_month)
    payload = {
        "metadata": {
            "herd_period": f"{int(herd['year'].min())}-{int(herd['year'].max())}",
            "slaughter_period": (
                f"{slaughter['period'].min().date()} a {slaughter['period'].max().date()}"
            ),
            "exports_period": (
                f"{exports['period'].min().date()} a {exports['period'].max().date()}"
            ),
            "sources": "IBGE SIDRA PPM 3939; IBGE SIDRA Abate 1092; Comex Stat/MDIC",
        },
        "executive_summary": [
            (
                f"Rebanho bovino em {indicators['latest_herd_year']}: "
                f"{indicators['herd_heads']:,.0f} cabecas "
                f"({indicators['herd_yoy_percent']:.1f}% vs. ano anterior)."
            ),
            (
                f"Lideranca geografica: {indicators['top_herd_state']} concentra "
                f"{indicators['top_herd_state_share_percent']:.1f}% do rebanho nacional."
            ),
            (
                f"Exportacao mais recente ({indicators['latest_export_period']}): "
                f"{indicators['net_weight_kg']:,.0f} kg; principal destino no ano: "
                f"{indicators['top_destination']}."
            ),
            (
                f"Concentracao de destinos: {indicators['destination_concentration']} "
                f"(HHI {concentration['hhi']:.0f})."
            ),
            (
                "Leitura estatistica: correlacao entre abate e exportacao e associativa, "
                "nao causal."
            ),
        ],
        "indicators": indicators,
        "concentration": concentration,
        "correlation": correlation,
        "data_quality": (
            pd.read_csv(quality_file).to_dict("records") if quality_file.exists() else []
        ),
        "herd_year": herd_year.to_dict("records"),
        "herd_state_year": herd_state_year.to_dict("records"),
        "slaughter_year": slaughter_year.to_dict("records"),
        "slaughter_quarter": slaughter_quarter.to_dict("records"),
        "exports_year": exports_year.to_dict("records"),
        "exports_month": exports_month.to_dict("records"),
        "destination_year": destination_year.to_dict("records"),
    }
    forecast_file = _path("models") / "forecast.csv"
    payload["forecast"] = (
        pd.read_csv(forecast_file).to_dict("records") if forecast_file.exists() else []
    )
    (out / "bovintel_dashboard.json").write_text(
        json.dumps(_json_safe(payload), default=str, allow_nan=False), encoding="utf-8"
    )
