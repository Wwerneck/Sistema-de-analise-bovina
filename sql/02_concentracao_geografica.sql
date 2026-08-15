WITH uf AS (
  SELECT year, state_name, SUM(bovine_herd_heads) AS heads
  FROM read_parquet('data/processed/herd_annual.parquet')
  GROUP BY 1, 2
),
shares AS (
  SELECT *, heads * 100.0 / SUM(heads) OVER (PARTITION BY year) AS share_percent
  FROM uf
)
SELECT
  year,
  state_name,
  heads,
  share_percent,
  SUM(share_percent * share_percent) OVER (PARTITION BY year) AS hhi
FROM shares
ORDER BY year, heads DESC;
