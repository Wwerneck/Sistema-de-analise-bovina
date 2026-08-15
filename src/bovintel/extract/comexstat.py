from __future__ import annotations

from pathlib import Path


def locate_comex_csv(raw_dir: Path) -> Path:
    candidates = sorted(raw_dir.glob("comex_exports*.csv"))
    if not candidates:
        raise FileNotFoundError(
            "Arquivo Comex Stat nao encontrado. Exporte CSV mensal para "
            "data/raw/comex_exports.csv com as colunas descritas em docs/fontes_de_dados.md."
        )
    return candidates[-1]
