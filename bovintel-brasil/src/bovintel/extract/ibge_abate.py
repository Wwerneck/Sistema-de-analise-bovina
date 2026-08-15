from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

SIDRA_URL = (
    "https://apisidra.ibge.gov.br/values/t/1092/n3/all/v/all/p/all/c12716/115236/c12529/118225"
)


def extract_abate_raw(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "ibge_abate.csv"
    if target.exists():
        return target
    response = requests.get(SIDRA_URL, timeout=60)
    response.raise_for_status()
    pd.DataFrame(response.json()).to_csv(target, index=False)
    return target
