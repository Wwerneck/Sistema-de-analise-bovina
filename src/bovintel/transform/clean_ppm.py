from __future__ import annotations

import pandas as pd

REQUIRED = {
    "year",
    "state_code",
    "state_name",
    "municipality_code",
    "municipality_name",
    "bovine_herd_heads",
}

UF_NAMES = {
    "11": "Rondônia",
    "12": "Acre",
    "13": "Amazonas",
    "14": "Roraima",
    "15": "Pará",
    "16": "Amapá",
    "17": "Tocantins",
    "21": "Maranhão",
    "22": "Piauí",
    "23": "Ceará",
    "24": "Rio Grande do Norte",
    "25": "Paraíba",
    "26": "Pernambuco",
    "27": "Alagoas",
    "28": "Sergipe",
    "29": "Bahia",
    "31": "Minas Gerais",
    "32": "Espírito Santo",
    "33": "Rio de Janeiro",
    "35": "São Paulo",
    "41": "Paraná",
    "42": "Santa Catarina",
    "43": "Rio Grande do Sul",
    "50": "Mato Grosso do Sul",
    "51": "Mato Grosso",
    "52": "Goiás",
    "53": "Distrito Federal",
}


def clean_herd(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: c.strip().lower() for c in df.columns}).copy()
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"herd_annual sem colunas obrigatorias: {sorted(missing)}")
    df["year"] = df["year"].astype(int)
    df["state_code"] = df["state_code"].astype(str).str.zfill(2)
    df["state_name"] = df["state_code"].map(UF_NAMES).fillna(df["state_name"])
    df["municipality_code"] = df["municipality_code"].astype(str).str.zfill(7)
    df["bovine_herd_heads"] = pd.to_numeric(df["bovine_herd_heads"], errors="coerce")
    return df[list(REQUIRED)]
