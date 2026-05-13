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

## Configurações testadas

| Config | Pop. | pc  | pm    | Seleção   | Crossover |
|--------|------|-----|-------|-----------|-----------|
| A      | 50   | 0.8 | 0.01  | Torneio   | 1 ponto   |
| B      | 50   | 0.8 | 0.05  | Torneio   | 1 ponto   |
| C      | 100  | 0.8 | 0.01  | Torneio   | 1 ponto   |
| D      | 100  | 0.9 | 0.01  | Torneio   | 2 pontos  |
| E      | 100  | 0.8 | 0.01  | Roleta    | 1 ponto   |
| F      | 200  | 0.8 | 0.01  | Torneio   | 1 ponto   |
| G      | 100  | 0.6 | 0.02  | Torneio   | 2 pontos  |

Cada configuração é executada **30 vezes** de forma independente. São reportados média e desvio padrão do melhor fitness e do número de gerações.

## Como executar

```bash
cd Tp2_Fund_Ia
python mochila_ag.py
```
