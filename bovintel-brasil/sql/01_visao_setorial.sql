CREATE OR REPLACE VIEW visao_setorial_anual AS
SELECT
  h.year,
  h.state_code,
  h.state_name,
  SUM(h.bovine_herd_heads) AS bovine_herd_heads
FROM read_parquet('data/processed/herd_annual.parquet') h
GROUP BY 1, 2, 3
ORDER BY 1, 4 DESC;
