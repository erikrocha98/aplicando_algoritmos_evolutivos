# TP2 — Fundamentos de IA: Problema da Mochila com Algoritmo Genético

## Problema

Instância com **50 itens** e capacidade **C = 14.239**. Objetivo: maximizar o valor total dos itens selecionados sem exceder a capacidade.

```
Maximizar:   sum(p_i * x_i)
Sujeito a:   sum(w_i * x_i) <= C,   x_i ∈ {0, 1}
```

## Estrutura do projeto

```
Tp2_Fund_Ia/
├── mochila_ag.py   # implementação do AG
└── mochila.txt     # instância do problema
```

## O que foi implementado

| Componente | Descrição |
|---|---|
| `load_data()` | Lê `mochila.txt` e retorna n, C, lucros e pesos |
| `init_population()` | Inicialização aleatória — cromossomo binário de 50 bits |
| `fitness()` | Penalidade dinâmica para soluções inválidas |
| `repair()` | Operador de reparo (implementado para comparação) |
| `select_tournament()` | Seleção por torneio (k=2) |
| `select_roulette()` | Seleção por roleta |
| `crossover_1pt()` / `crossover_2pt()` | Cruzamento de 1 e 2 pontos |
| `mutate()` | Mutação bit-flip por gene |
| `run_ga()` | Loop principal com elitismo e parada por estagnação |
| `run_experiments()` | Roda 7 configurações × 30 execuções e imprime tabela de resultados |

## Tratamento de soluções inválidas

Foram implementadas duas abordagens, controladas pelo flag `use_repair` no `GAConfig`:

**Penalidade dinâmica** (abordagem padrão, `use_repair=False`):
```
fitness = valor_total - alpha * max(0, peso_total - C)
```
onde `alpha = 2 * max(p_i / w_i)`, garantindo que qualquer solução inválida tenha fitness menor que qualquer solução válida.

**Operador de reparo** (`use_repair=True`): remove iterativamente os itens com pior razão p/w até que o peso respeite a capacidade.

### Justificativa da escolha

A penalidade dinâmica foi adotada como abordagem principal por preservar a diversidade genética: soluções temporariamente inválidas permanecem na população e contribuem para a exploração do espaço de busca, guiando gradualmente a população para a região viável. O operador de reparo, embora produza sempre soluções viáveis, reduz a diversidade ao forçar todas as soluções para a fronteira de viabilidade desde cedo, podendo levar a convergência prematura.

## Estrutura do projeto (atualizada)

```
Tp2_Fund_Ia/
├── mochila_ag.py          # implementação do AG
├── experimentos.py        # bateria de experimentos sistemáticos
├── mochila.txt            # instância do problema
├── resultados_runs.csv    # uma linha por execução (1620 linhas)
└── resultados_resumo.csv  # média/dp por configuração (54 linhas)
```

## Experimentos realizados

Grade completa testada (54 configurações × 30 execuções = **1.620 runs**):

| Parâmetro | Valores testados |
|---|---|
| Tamanho de população | 50, 100, 200 |
| Probabilidade de cruzamento (pc) | 0.6, 0.8, 0.9 |
| Probabilidade de mutação (pm) | 0.01, 0.03, 0.05 |
| Tipo de seleção | Torneio k=3, Roleta |

Crossover fixado em 1 ponto. Máximo de 500 gerações, parada por estagnação em 50 gerações sem melhora.

### Top 5 configurações (melhor lucro global)

| Configuração | Pop. | pc | pm | Seleção | Melhor Lucro | Fit. Média | DP | Gen. Média |
|---|---|---|---|---|---|---|---|---|
| pop200_pc0.6_pm0.01_tournament_k3 | 200 | 0.6 | 0.01 | Torneio k=3 | **15.757** | 15.633,80 | 91,62 | 152,67 |
| pop200_pc0.9_pm0.01_tournament_k3 | 200 | 0.9 | 0.01 | Torneio k=3 | 15.747 | **15.668,63** | **54,55** | 141,80 |
| pop200_pc0.8_pm0.01_tournament_k3 | 200 | 0.8 | 0.01 | Torneio k=3 | 15.743 | 15.645,97 | 65,59 | 143,87 |
| pop100_pc0.6_pm0.01_tournament_k3 | 100 | 0.6 | 0.01 | Torneio k=3 | 15.741 | 15.555,00 | 106,40 | 146,90 |
| pop200_pc0.9_pm0.03_tournament_k3 | 200 | 0.9 | 0.03 | Torneio k=3 | 15.741 | 15.583,00 | 70,53 | 147,80 |

### Conclusões dos experimentos

**Torneio (k=3) supera a roleta consistentemente.** O melhor resultado da roleta foi 15.638, contra 15.757 do torneio. A roleta perde pressão seletiva quando os valores de fitness são próximos entre si, o que ocorre naturalmente nas gerações finais.

**Mutação baixa (pm=0.01) é o fator mais crítico.** Todos os top 5 usam pm=0.01. pm=0.05 produziu os piores resultados em praticamente todas as combinações — a alta taxa de bit-flip desfaz boas soluções mais rápido do que a seleção consegue preservá-las.

**População maior melhora o melhor global, mas não garante menor variância.** pop=200 domina o topo em lucro máximo, porém `pop200_pc0.9_pm0.01` apresentou o menor desvio padrão (54,55), sendo a configuração mais estável e com melhor média — a recomendada para uso final.

**Taxa de cruzamento tem impacto secundário.** pc=0.6, 0.8 e 0.9 aparecem no top 5, indicando que o AG é robusto a esse parâmetro dentro da faixa testada.

### Configuração recomendada

| Parâmetro | Valor |
|---|---|
| População | 200 |
| pc | 0.9 |
| pm | 0.01 |
| Seleção | Torneio k=3 |
| Crossover | 1 ponto |
| Melhor lucro global | 15.747 |
| Média das 30 execuções | 15.668,63 |
| Desvio padrão | 54,55 |

## Como executar

```bash
cd Tp2_Fund_Ia

# rodar a bateria completa de experimentos
python3 experimentos.py

# rodar apenas o AG com parâmetros customizados
python3 mochila_ag.py
```
