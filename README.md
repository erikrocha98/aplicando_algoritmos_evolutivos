# TP2 — Fundamentos de IA

Implementação de dois algoritmos evolucionários:

- **Algoritmo Genético (AG)** — resolve o Problema da Mochila 0/1 (50 itens, capacidade C = 14.239) com penalidade dinâmica para soluções inválidas. A bateria de experimentos testa 54 configurações (tamanho de população, pc, pm, tipo de seleção) com 30 execuções cada.
- **Evolução Diferencial (ED)** — variante DE/rand/1/bin para minimizar a função esfera em 10 dimensões. A bateria de experimentos testa combinações de população, fator de escala F e taxa de cruzamento CR com 30 execuções cada.

## Como executar

```bash
cd Tp2_Fund_Ia
```

### Algoritmo Genético (Mochila)

```bash
# rodar o AG com os parâmetros definidos em mochila_ag.py
python3 mochila_ag.py

# rodar a bateria completa de experimentos (gera resultados_runs.csv e resultados_resumo.csv)
python3 experimentos.py

# gerar gráficos a partir dos CSVs
python3 graficos.py
```

### Evolução Diferencial (Função Esfera)

```bash
# demo com parâmetros padrão
python3 ed_esfera.py demo

# rodar a bateria de experimentos (gera resultados_ed.csv)
python3 ed_esfera.py experiment --output resultados_ed.csv --progress

# executar os testes automatizados
python3 ed_esfera.py test
```
