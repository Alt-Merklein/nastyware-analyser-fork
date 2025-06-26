
# Performance Test 3

>Extração paralela & leitura seletiva do PE
>
## Descrição geral

Acelera o **último gargalo**: extração de features. Duas modificações principais:

1. **Paralelização** – `ProcessPoolExecutor`, `n_jobs = CPUs−1`, `chunksize = 64`.  
2. **Leitura seletiva** – `pefile.PE(fast_load=True)` seguido de `parse_data_directories([...IMPORT])` extrai **apenas** a tabela de imports.

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

- **`performance_test_utils.py`**  
  *Nova função `_extract_one(fp)` lê somente dados necessários e devolve vetor.  
  * Função `export_files_imports` coordena parallel map e escrita de saída.  
  * `_core_name` normaliza nomes (`g-`/`r-`) antes de salvar.
- Todos os aprimoramentos de Pipelines 1–2 mantidos (matriz incremental + dedup).

## Fundamentação teórica

- Ler só a **tabela de imports** preserva poder discriminativo e reduz CPU/IO.  
- *Process-based* paralelização contorna **GIL** do Python; chunksize balanceia overhead de fork vs trabalho por tarefa.  

## Resultados observados

### Resumo estatístico (75 repetições)

| Métrica                      | Mean   | SE     | Min. | 25%   | Median | 75%   | Max.  |
| ---------------------------- | ------ | ------ | ---- | ----- | ------ | ----- | ----- |
| features_extraction_time (s) | 0.78   | 0.13   | 0.67 | 0.71  | 0.74   | 0.79  | 1.27  |
| coss_distance_time (s)       | 0.71   | 0.21   | 0.34 | 0.51  | 0.74   | 0.92  | 1.06  |
| damicore_time (s)            | 20.48  | 12.31  | 3.39 | 8.69  | 19.60  | 32.36 | 42.10 |
| total_time (s)               | 33.37  | 19.31  | 6.62 | 14.81 | 31.73  | 51.82 | 68.39 |
|                              |        |        |      |       |        |       |       |
| duplicated_vectors           | 506.80 | 317.39 | 34   | 211   | 487    | 792   | 1043  |
| unique_vectors               | 460.20 | 119.09 | 233  | 356   | 480    | 575   | 624   |

**Aceleração vs baseline:** ×46.5

- **features_extraction_time** médio caiu de 77 s → **0.78 s** (≈ 99×).

- **coss_distance_time** médio caiu de 1216 s → **0.71 s** (≈ 1717×).
- **damicore_time** médio caiu de 249 s → **20.48 s** (≈ 12×).
- Tempo total médio é **46×** mais baixo que o baseline.

## Limitações

- Uso de múltiplos processos aumenta consumo de RAM (cópia de vetores em cada worker).  
- I/O simultâneo pode se tornar gargalo em discos lentos.  
- Código assume que todos os binários têm seção de imports bem‑formada; falhas precisam de try/except para produção.
