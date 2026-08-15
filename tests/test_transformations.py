import pandas as pd

from bovintel.transform.clean_abate import clean_slaughter
from bovintel.transform.clean_comex import clean_exports


def test_export_price_and_period():
    df = pd.DataFrame(
        [
            {
                "year": 2024,
                "month": 2,
                "destination_country": "China",
                "ncm_code": "0202",
                "export_value_usd_fob": 100,
                "net_weight_kg": 20,
            }
        ]
    )
    out = clean_exports(df)
    assert out.loc[0, "avg_export_price_usd_per_kg"] == 5
    assert str(out.loc[0, "period"].date()) == "2024-02-01"


def test_carcass_weight_zero_safe():
    df = pd.DataFrame(
        [
            {
                "year": 2024,
                "quarter": 1,
                "state_code": "35",
                "state_name": "Sao Paulo",
                "slaughtered_heads": 0,
                "carcass_weight_kg": 0,
            }
        ]
    )
    out = clean_slaughter(df)
    assert pd.isna(out.loc[0, "avg_carcass_weight_kg_per_head"])
