from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px


def save_figures(herd: pd.DataFrame, exports: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    herd_br = herd.groupby("year", as_index=False)["bovine_herd_heads"].sum()
    px.line(herd_br, x="year", y="bovine_herd_heads", title="Efetivo bovino nacional").write_html(
        out_dir / "herd_national.html"
    )
    exp = exports.groupby("period", as_index=False)[["net_weight_kg", "export_value_usd_fob"]].sum()
    px.line(
        exp, x="period", y="net_weight_kg", title="Exportacao mensal - peso liquido"
    ).write_html(out_dir / "exports_volume.html")
