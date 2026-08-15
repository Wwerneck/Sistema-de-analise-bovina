# AgroBov Analytics

Dashboard e pipeline de dados para inteligencia setorial da pecuaria bovina brasileira. O projeto integra bases oficiais de rebanho, abate e exportacoes para analisar escala produtiva, concentracao geografica, dependencia de destinos externos, qualidade dos dados, associacao estatistica e previsao simples de curto prazo.

## Destaques

- Pipeline Python reproduzivel com etapas de transformacao, validacao, analise, previsao e exportacao para dashboard.
- Dados oficiais de IBGE SIDRA PPM, IBGE SIDRA Abate e Comex Stat/MDIC.
- Dashboard executivo em HTML, CSS e JavaScript puro, com Chart.js local.
- Tema visual Executive Dark Analytics para os paineis analiticos.
- KPIs dinamicos por ano, rankings, donuts de composicao, series temporais, concentracao comercial, qualidade dos dados e correlacao.
- Capturas prontas para apresentacao e LinkedIn em `captures/linkedin/`.

## Capturas

As imagens finais para divulgacao estao em:

- `captures/linkedin/01-hero-kpis.png`
- `captures/linkedin/02-composicao.png`
- `captures/linkedin/03-producao.png`
- `captures/linkedin/04-mercado-diagnostico.png`
- `captures/linkedin/05-diagnostico.png`

## Perguntas de negocio

- Como o rebanho bovino evolui no Brasil?
- Quais UFs concentram a atividade pecuaria?
- Como evoluem abate, peso medio de carcaca, exportacoes e destinos?
- Qual a dependencia dos principais mercados compradores?
- Ha associacao estatistica entre abate e exportacao?
- Qual a previsao simples para seis meses de volume exportado?

## Fontes de dados

Fontes oficiais prioritarias:

- IBGE SIDRA PPM, tabela 3939.
- IBGE SIDRA Abate, tabela 1092.
- Comex Stat/MDIC.

Na ultima execucao local, a cobertura utilizada foi:

- Rebanho: 2015-2024.
- Abate: 2015-2026.
- Exportacoes: 2015-01 a 2026-07.

Consulte tambem:

- `docs/fontes_de_dados.md`
- `docs/dicionario_de_dados.md`
- `config/data_sources.yaml`

## Arquitetura

```text
config/                 Parametros e fontes
data/raw/               CSVs oficiais locais
data/processed/         Bases tratadas em Parquet
docs/                   Documentacao tecnica
outputs/                Tabelas, figuras e modelos
scripts/                Scripts de pipeline e exportacao
sql/                    Consultas analiticas DuckDB
src/bovintel/           Codigo Python do projeto
dashboard/              Aplicacao web estatica
captures/linkedin/      Imagens para apresentacao
tests/                  Testes automatizados
```

## Stack

- Python 3.11
- pandas, numpy e pyarrow
- DuckDB SQL
- scipy e statsmodels
- pytest
- HTML, CSS e JavaScript
- Chart.js local em `dashboard/assets/vendor/chart.umd.js`

## Execucao do pipeline

```bash
make setup
make transform
make validate
make analyze
make forecast
make dashboard
```

Caso a extracao automatica nao esteja disponivel no ambiente, coloque os CSVs oficiais em `data/raw/`:

- `herd_annual.csv`
- `slaughter_quarterly.csv`
- `comex_exports.csv`

Os layouts esperados estao descritos em `docs/dicionario_de_dados.md`.

## Executar a dashboard

Sirva a pasta `dashboard/` por HTTP local:

```bash
python -m http.server 8000 -d dashboard
```

Depois abra:

```text
http://localhost:8000
```

## Dashboard

A dashboard inclui:

- filtro de ano do rebanho;
- resumo de destaques do recorte ativo;
- cards de KPI com variacao dinamica;
- composicao geografica por UF;
- mix dos destinos de exportacao;
- evolucao do rebanho nacional;
- ranking de UFs;
- abate trimestral;
- exportacoes mensais;
- ranking de destinos;
- indicadores de concentracao comercial;
- qualidade dos dados;
- associacao abate-exportacao;
- previsao de curto prazo.

## SQL

Execute consultas com DuckDB:

```bash
duckdb -c ".read sql/01_visao_setorial.sql"
```

Os arquivos SQL cobrem visao setorial anual, concentracao geografica do rebanho e destinos das exportacoes.

## Testes

```bash
pytest
```

Os testes cobrem transformacoes, qualidade de dados, concentracao e previsao.

## Limitacoes

- As series possuem periodicidades diferentes: rebanho anual, abate trimestral e exportacoes mensais.
- Correlacao mede associacao estatistica, nao causalidade.
- Meses sem observacao nao sao preenchidos artificialmente com zero.
- Amostras sinteticas existem apenas em `tests/fixtures/` para testes automatizados.

## Competencias demonstradas

- Engenharia de dados com Python.
- Tratamento e validacao de bases oficiais.
- SQL analitico com DuckDB.
- Indicadores de concentracao como CR3, CR5, HHI e Pareto.
- Estatistica aplicada e correlacao.
- Baseline de previsao de series temporais.
- Dashboard executivo com front-end puro.
- Visualizacao de dados com foco em clareza, contraste e comunicacao profissional.
