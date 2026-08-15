from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def settings() -> dict[str, Any]:
    return load_yaml(ROOT / "config" / "settings.yaml")


def ensure_dirs() -> None:
    cfg = settings()
    for value in cfg["paths"].values():
        Path(value).mkdir(parents=True, exist_ok=True)
