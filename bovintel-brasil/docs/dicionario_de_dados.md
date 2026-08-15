# Dicionario de dados

## herd_annual

`year`, `state_code`, `state_name`, `municipality_code`, `municipality_name`, `bovine_herd_heads`.

## slaughter_quarterly

`year`, `quarter`, `period`, `state_code`, `state_name`, `slaughtered_heads`, `carcass_weight_kg`, `avg_carcass_weight_kg_per_head`.

## exports_monthly

`year`, `month`, `period`, `destination_country`, `ncm_code`, `export_value_usd_fob`, `net_weight_kg`, `avg_export_price_usd_per_kg`.

Valores ausentes, zeros reais, dado suprimido e dado nao disponivel devem permanecer distinguiveis. O relatorio `outputs/tables/data_quality_report.csv` possui colunas separadas para `zero_numeric_cells`, `missing_cells`, `raw_suppressed_symbols` e `raw_unavailable_symbols`.
