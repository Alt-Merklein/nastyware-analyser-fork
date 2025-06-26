# Performance Test - n. 1

> Mantém o mesmo conjunto de dados usado no pipeline 0 (baseline Saucy Spice), mas:
>
> - Reaproveita a matriz de distâncias de rodadas anteriores.  
> - Abole o overhead de abrir/fechar um *pool* por linha da matriz.
>
## Descrição geral

Implementa **duas melhorias críticas** sobre o baseline (pipeline 0):

1. **Paralelização inteligente do cálculo de distâncias**  
   – um único `Pool` é criado e mantido durante toda a etapa;  
   – os vetores já carregados ficam em memória partilhada (função `init_pool`).
2. **Atualização incremental da matriz de distância**  
   – se existe um arquivo `*.phylip` anterior, só são calculadas  *distâncias novas × antigas* (n·k) e *novas × novas* (k²∕2).  
   – complexidade assintótica passa de **O((n+k)²)** para **O(n·k + k²)**.

Esperamos duas ordens de magnitude de ganho na **primeira rodada** e até três ordens quando o número de amostras extras cresce.

## Parâmetros do teste

Este teste ocorreu com:

- 300 amostras de goodware
- 1 amostra inicial de malware
- 0 amostras extras iniciais de malware
- 100 amostras extras de malware por rodada
- 5 repetições para cada N amostras extras
- 0.9 de split ratio para train/test

Foram gerados 75 eventos no total (5 rodadas para cada N amostras).

## Configuração dos scripts utilizados

| Arquivo                          | Alteração relevante                                                        |
| -------------------------------- | -------------------------------------------------------------------------- |
| `create_phylip_coss_distance.py` | + `load_vectors_from_files` (leitura única); + `init_pool(vectors)` – põe vetores em `global _V`; + `create_dist_matrix_from_zero()` – *um* `Pool` para todo o grid; + `update_existing_matrix()` – computa apenas `n·k + k²/2` pares faltantes.                                                                                                      |
| `run_performance_test.py`        | Passa `input_matrix` e `output_matrix`, acionando o modo incremental.      |
| `run_performance_test.sh`        | Apenas redireciona para o diretório `pipelines/performance_test_1/…`.      |

## Fundamentação Teórica

- **Cálculo incremental de matrizes de distância** [Gower 1966] mostra que, fornecida uma sub‑matriz previamente computada, basta avaliar as entradas da última linha/coluna acrescentadas — custo linear no nº de novos vetores (*nk*) mais o custo quadrático interno (*k²*).
- **Paralelismo estável**: manter processos vivos evita custos de “fork+warm‑up” e melhora o *cache locality* ao partilhar vetores carregados na memória do worker (justificativa empírica de Xu 2021 sobre *pool longevity*).

## Resultados Observados  

### Resumo estatístico (75 repetições)

| Métrica                      | Mean   | SE     | Min.  | 25%   | Median | 75%    | Max.   |
| ---------------------------- | ------ | ------ | ----- | ----- | ------ | ------ | ------ |
| features_extraction_time (s) | 76.67  | 26.35  | 30.64 | 53.39 | 78.92  | 100.96 | 116.32 |
| coss_distance_time (s)       | 1.97   | 1.14   | 0.40  | 0.92  | 1.81   | 2.96   | 4.07   |
| damicore_time (s)            | 250.31 | 252.53 | 4.32  | 30.96 | 152.96 | 440.75 | 818.96 |
| total_time (s)               | 338.72 | 282.80 | 37.09 | 90.14 | 243.41 | 560.43 | 956.98 |

**Aceleração vs baseline:** ×4.58

- **coss_distance_time** médio despencou de 1216 s para 1.97 s** (≈ 618×).
- Tempo total médio é 4.58×** mais baixo que o baseline.

*Primeira rodada* (k ≈ 0): ganho dominado pela **paralelização** (114 s → 0,40 s ≈ 278×).  
*Rodadas posteriores* (k ≈ 1 400): benefício adicional da **incrementalidade** elevou o ganho para **727×**.

## Limitações

- A matriz continua guardada em **RAM** completa; datasets gigantes (> 50 k) ainda podem estourar memória.
- **Balanceamento de carga** fixa (`chunksize=default`) pode gerar filas vazias em cenários com vetores muito heterogêneos em tamanho.
