# Metodologia

As analises agregam dados oficiais em granularidades anuais, trimestrais e mensais. Percentuais usam denominador positivo; divisoes por zero retornam valor ausente.

O tratamento de lacunas separa quatro casos: zero numerico observado, valor ausente apos processamento, valor suprimido no bruto (`X`) e dado nao disponivel no bruto (`...`). Zeros nao sao usados para preencher lacunas; cada classe aparece separadamente em `outputs/tables/data_quality_report.csv`.

HHI e calculado por `sum(share_percent^2)`, em escala de 0 a 10.000. A classificacao usada e: abaixo de 1.500 baixa concentracao, 1.500 a 2.499 concentracao moderada e 2.500 ou mais alta concentracao.

Correlacoes de Pearson e Spearman so sao calculadas com pelo menos tres pares validos. O resultado e associativo e nao demonstra causalidade.

A previsao compara baseline sazonal ingenuo com Holt-Winters quando ha serie suficiente. O melhor modelo e escolhido por MAE, com RMSE e MAPE reportados.

O dashboard usa agregacoes pre-calculadas no pipeline para evitar processamento pesado no navegador. Os cards misturam conscientemente periodicidades diferentes: rebanho usa o ultimo ano PPM, abate usa o ultimo trimestre disponivel e exportacoes usam o ultimo mes Comex Stat.
