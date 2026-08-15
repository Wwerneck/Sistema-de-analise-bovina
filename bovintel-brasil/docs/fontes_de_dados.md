# Fontes de dados

Extraido em: 2026-08-14.

## IBGE PPM

- Fonte: IBGE SIDRA, Pesquisa da Pecuaria Municipal.
- Tabela confirmada: 3939, "Efetivo dos rebanhos, por tipo de rebanho".
- URL: https://sidra.ibge.gov.br/tabela/3939
- Filtro: variavel efetivo dos rebanhos, tipo de rebanho bovino, anos desde 2015, municipio e UF.
- Unidade: cabecas.
- Cobertura local baixada: 2015-2024.

## IBGE Abate

- Fonte: IBGE SIDRA, Pesquisa Trimestral do Abate de Animais.
- Tabela confirmada: 1092, quantidade e peso total das carcacas dos bovinos abatidos.
- URL: https://sidra.ibge.gov.br/tabela/1092
- Cobertura confirmada em pagina IBGE/SIDRA: Brasil e UF, periodicidade trimestral.
- Unidade: cabecas abatidas e kg de carcaca.
- Cobertura local baixada: 2015-2026.

## Comex Stat / MDIC

- Fonte: Comex Stat.
- URL: https://comexstat.mdic.gov.br/pt/home
- Filtro padrao: exportacoes brasileiras mensais dos NCMs configurados em `config/settings.yaml`, pais de destino e, quando disponivel, UF.
- Unidade: US$ FOB e kg liquido.
- Cobertura local baixada: 2015-01 a 2026-07.

## Importacao manual

Quando a API nao estiver acessivel, exporte CSVs oficiais para `data/raw/` com os nomes e colunas do dicionario. Dados brutos grandes estao no `.gitignore`.
