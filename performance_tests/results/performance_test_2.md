# Performance Test - n. 2

> Deduplicação de vetores & métricas de unicidade
>
## Descrição geral

Além da matriz incremental herdada do Pipeline 1, introduz **deduplicação** dos vetores de importação, removendo entradas idênticas antes do cálculo da matriz. Passa também a reportar `unique_vectors` e `duplicated_vectors` no CSV.

## Parâmetros do teste

Este teste ocorreu com:
   300 amostras de goodware

- 1 amostra inicial de malware
- 0 amostras extras iniciais de malware
- 100 amostras extras de malware por rodada
- 5 repetições para cada N amostras extras
- 0.9 de split ratio para train/test

Foram gerados 75 eventos no total (5 rodadas para cada N amostras).

## Configuração dos scripts utilizados

- **`export_new_format_import_files.py`**  
  * Função `delete_duplicates(dir)` remove arquivos duplicados com base no conteúdo textual (string de 0s e 1s)
- **`run_performance_test.py`**  
  *Calcula `unique_vectors = len(TRAIN_FORMATTED_IMPORT_DIR)`  
  * Calcula `duplicated_vectors = train_raw_samples - unique_vectors`  
  * Esses valores vão para o CSV e são lidos na análise.  
- Demais componentes idênticos ao Pipeline 1.

## Fundamentação teórica

Em coleções grandes de amostras malware/goodware, múltiplos binários têm mesma lista de imports (empacotadores, variantes triviais). Remover duplicatas diminui custo computacional sem perda de informação para clustering baseado em imports (variável binária).

## Resultados observados

### Resumo estatístico (75 repetições)

| Métrica                      | Mean   | SE     | Min.  | 25%   | Median | 75%    | Max.   |
| ---------------------------- | ------ | ------ | ----- | ----- | ------ | ------ | ------ |
| features_extraction_time (s) | 77.53  | 27.78  | 30.40 | 52.65 | 78.48  | 100.64 | 122.39 |
| coss_distance_time (s)       | 0.72   | 0.23   | 0.35  | 0.51  | 0.74   | 0.93   | 1.13   |
| damicore_time (s)            | 20.78  | 13.10  | 3.31  | 8.52  | 19.06  | 32.20  | 45.30  |
| total_time (s)               | 110.73 | 48.08  | 35.88 | 66.57 | 109.49 | 152.44 | 194.09 |
|                              |        |        |       |       |        |        |        |
| duplicated_vectors           | 506.80 | 317.39 | 34    | 211   | 487    | 792    | 1043   |
| unique_vectors               | 460.20 | 119.09 | 233   | 356   | 480    | 575    | 624    |

**Aceleração vs baseline:** ×14.01

- **damicore_time** médio despencou de 249 s para **20.78 s** (≈ 12×) porque há menos vetores para clusterizar.

- Tempo total médio é **14×** mais baixo que o baseline.

## Limitações

- Relevância da deduplicação depende da redundância real do dataset.  
- Extração de features continua gargalo.
