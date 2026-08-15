# Arquitetura

`src/bovintel` concentra codigo de configuracao, extracao, transformacao, analise, modelos, visualizacao e pipeline. `config/` centraliza parametros. `data/raw/` guarda arquivos oficiais locais e nao versionados. `data/processed/` recebe Parquet. `outputs/` guarda tabelas, figuras e modelos. `dashboard/` consome JSON pequeno exportado pelo pipeline.
