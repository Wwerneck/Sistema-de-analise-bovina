WITH dest AS (
  SELECT
    year,
    destination_country,
    SUM(net_weight_kg) AS net_weight_kg,
    SUM(export_value_usd_fob) AS export_value_usd_fob
  FROM read_parquet('data/processed/exports_monthly.parquet')
  GROUP BY 1, 2
)
SELECT
  *,
  net_weight_kg * 100.0 / SUM(net_weight_kg) OVER (PARTITION BY year) AS volume_share_percent
FROM dest
ORDER BY year, net_weight_kg DESC;
