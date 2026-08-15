from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

SIDRA_URL = "https://apisidra.ibge.gov.br/values/t/3939/n6/all/v/105/c79/2670/p/all"


def extract_ppm_raw(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "ibge_ppm_herd.csv"
    if target.exists():
        return target
    response = requests.get(SIDRA_URL, timeout=60)
    response.raise_for_status()
    pd.DataFrame(response.json()).to_csv(target, index=False)
    return target
