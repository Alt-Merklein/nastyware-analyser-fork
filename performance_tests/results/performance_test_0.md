# Performance Test - n. 0

> Baseline (Saucy Spice original)

## Descrição geral

Pipeline **sem otimizações**: replica o fluxo original descrito no artigo *“Saucy Spice: An Efficient Signature‑Generation Approach…”*. Todos os arquivos PE são processados **um‑a‑um** de forma **serial**, extraindo o cabeçalho completo antes de vetorizá‑lo. A matriz de distância (similaridade de cosseno) é recalculada **integralmente** a cada rodada, resultando em complexidade **O(m²)** para *m* vetores de importação.

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

- **`run_performance_test.sh`** – configura o experimento e dá início ao pipeline automatizado.  
- **`run_performance_test.py`**  
  1. `export_files_imports` → percorre cada arquivo, faz `pefile.PE()` e grava *todas* as DLL/Funções.  
  2. `create_phylip_coss_distance` → carrega todos os vetores em memória e gera a matriz de distância completa.  
  3. `damicore.py` → clusteriza as amostras com base na matriz de distância
  4. Gera regras YARA.  
- Métricas `duplicated` / `unique` no CSV final permanecem em **0** porque não há deduplicação.

## Fundamentação teórica

Assume que a **lista completa de imports** é representativa do comportamento do executável (base em linhas de pesquisa que usam API‑Calls).

## Resultados observados

### Resumo estatístico (75 repetições)

| Métrica                  | Média (s) | Mediana (s) |
| ------------------------ | --------- | ----------- |
| Features Extraction Time | 76.28     | 77.90       |
| Coss Distance Time       | 1216.05   | 1003.20     |
| Total Time               | 1551.75   | 1242.41     |

## Limitações

- Custo quadrático de tempo e memória para matriz de distância.  
  - Distâncias de cosseno entre vetores binários são proporcionalmente caras: necessidade de ½·m·(m−1) comparações.
- Extração de features lê o PE inteiro → alto overhead de I/O + parsing.  
- Não detecta duplicatas; esforço desperdiçado.
