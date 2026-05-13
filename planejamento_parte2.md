# Planejamento — Parte 2: Problema da Mochila (Algoritmo Genético)

## 1. Descrição do Problema

**Instância:** `mochila.txt`
- **n = 50** itens
- **C = 14239** (capacidade máxima da mochila)
- Cada item i possui: valor `p_i` e peso `w_i`

**Objetivo:** maximizar o valor total dos itens selecionados sem exceder a capacidade C.

### Modelo Matemático

```
Maximizar:   sum(p_i * x_i)  para i = 1..n
Sujeito a:   sum(w_i * x_i) <= C
             x_i ∈ {0, 1}
```

---

## 2. Representação (Cromossomo)

- Cromossomo binário de comprimento **n = 50**
- `x_i = 1` → item i é levado
- `x_i = 0` → item i é deixado
- Inicialização: aleatória, com 0s e 1s uniformes

---

## 3. Função de Aptidão (Fitness)

### Estratégia: Penalidade dinâmica

Para soluções **válidas** (peso ≤ C):
```
fitness(x) = sum(p_i * x_i)
```

Para soluções **inválidas** (peso > C):
```
fitness(x) = sum(p_i * x_i) - alpha * max(0, sum(w_i * x_i) - C)
```

- `alpha` é um fator de penalidade (a calibrar; sugestão inicial: `alpha = max(p_i / w_i)`)
- A penalidade torna soluções inválidas piores que qualquer solução válida, guiando a busca para a região viável

**Alternativa (operador de reparo):** se a mochila estiver com excesso de peso, remover iterativamente o item com menor razão `p_i / w_i` até que a solução seja viável. Esta abordagem será testada em comparação com a penalidade.

---

## 4. Operadores Genéticos

### 4.1 Seleção

Implementar **dois métodos** para comparação:

| Método | Descrição |
|--------|-----------|
| **Torneio** (k=2 ou k=3) | Sorteia k indivíduos, seleciona o melhor |
| **Roleta** | Probabilidade proporcional ao fitness |

Indivíduos selecionados **não são removidos** do pool (seleção com reposição).

### 4.2 Cruzamento (Crossover)

Implementar e comparar:

| Método | Descrição |
|--------|-----------|
| **1 ponto** | Ponto de corte sorteado aleatoriamente |
| **2 pontos** | Dois pontos de corte, troca o segmento central |

Parâmetro `pc` (probabilidade de cruzamento): a ser variado nos experimentos.

### 4.3 Mutação

- **Bit-flip**: para cada gene, com probabilidade `pm`, inverte o bit (0→1 ou 1→0)
- Garante diversidade genética e evita convergência prematura
- Parâmetro `pm` (probabilidade de mutação): a ser variado nos experimentos

---

## 5. Elitismo

- Preservar o **melhor indivíduo** de cada geração (elitismo simples)
- Evita perda do melhor resultado já encontrado

---

## 6. Critério de Parada

- Número máximo de gerações (ex.: 500 ou 1000)
- E/ou: sem melhora no melhor fitness por `k` gerações consecutivas (ex.: k = 50)

---

## 7. Configurações de Hiperparâmetros a Testar

Rodar **30 execuções independentes** por configuração para obter média e desvio padrão.

| Config | Pop. Size | `pc` | `pm` | Seleção | Crossover |
|--------|-----------|------|------|---------|-----------|
| A | 50 | 0.8 | 0.01 | Torneio | 1 ponto |
| B | 50 | 0.8 | 0.05 | Torneio | 1 ponto |
| C | 100 | 0.8 | 0.01 | Torneio | 1 ponto |
| D | 100 | 0.9 | 0.01 | Torneio | 2 pontos |
| E | 100 | 0.8 | 0.01 | Roleta | 1 ponto |
| F | 200 | 0.8 | 0.01 | Torneio | 1 ponto |
| G | 100 | 0.6 | 0.02 | Torneio | 2 pontos |

### Métricas a coletar por execução:
- Melhor fitness encontrado
- Número de gerações até convergência
- Peso total da solução final

### Estatísticas a reportar (sobre as 30 execuções):
- Média e desvio padrão do melhor fitness
- Média e desvio padrão do número de gerações
- Melhor solução global encontrada

---

## 8. Estrutura do Código Python

```
mochila_ag.py
├── load_data(path)              → n, C, profits, weights
├── init_population(pop_size, n) → population
├── fitness(individual, ...)     → float
├── repair(individual, ...)      → individual
├── select_tournament(pop, k)    → individual
├── select_roulette(pop)         → individual
├── crossover_1pt(p1, p2, pc)   → child1, child2
├── crossover_2pt(p1, p2, pc)   → child1, child2
├── mutate(individual, pm)       → individual
├── run_ga(config)               → results
└── main()                       → run experiments, print table
```

---

## 9. Itens do Problema (mochila.txt)

| Item | Valor (p) | Peso (w) | Razão p/w |
|------|-----------|----------|-----------|
| 1 | 906 | 845 | 1.07 |
| 2 | 748 | 758 | 0.99 |
| 3 | 337 | 421 | 0.80 |
| 4 | 223 | 259 | 0.86 |
| 5 | 514 | 512 | 1.00 |
| 6 | 492 | 405 | 1.21 |
| 7 | 705 | 784 | 0.90 |
| 8 | 314 | 304 | 1.03 |
| 9 | 519 | 477 | 1.09 |
| 10 | 594 | 584 | 1.02 |
| 11 | 972 | 909 | 1.07 |
| 12 | 513 | 505 | 1.02 |
| 13 | 375 | 282 | 1.33 |
| 14 | 777 | 756 | 1.03 |
| 15 | 637 | 619 | 1.03 |
| 16 | 240 | 251 | 0.96 |
| 17 | 777 | 756 | 1.03 |
| 18 | 637 | 619 | 1.03 |
| 19 | 240 | 251 | 0.96 |
| 20 | 929 | 910 | 1.02 |
| 21 | 960 | 983 | 0.98 |
| 22 | 826 | 811 | 1.02 |
| 23 | 861 | 903 | 0.95 |
| 24 | 249 | 311 | 0.80 |
| 25 | 667 | 730 | 0.91 |
| 26 | 922 | 899 | 1.03 |
| 27 | 715 | 684 | 1.05 |
| 28 | 468 | 473 | 0.99 |
| 29 | 19 | 101 | 0.19 |
| 30 | 487 | 435 | 1.12 |
| 31 | 687 | 611 | 1.12 |
| 32 | 999 | 914 | 1.09 |
| 33 | 1036 | 967 | 1.07 |
| 34 | 558 | 478 | 1.17 |
| 35 | 951 | 866 | 1.10 |
| 36 | 269 | 261 | 1.03 |
| 37 | 784 | 806 | 0.97 |
| 38 | 590 | 549 | 1.07 |
| 39 | 32 | 15 | 2.13 |
| 40 | 783 | 720 | 1.09 |
| 41 | 469 | 399 | 1.18 |
| 42 | 904 | 825 | 1.10 |
| 43 | 687 | 669 | 1.03 |
| 44 | 97 | 2 | 48.50 |
| 45 | 510 | 494 | 1.03 |
| 46 | 858 | 868 | 0.99 |
| 47 | 276 | 244 | 1.13 |
| 48 | 426 | 326 | 1.31 |
| 49 | 955 | 871 | 1.10 |
| 50 | 251 | 192 | 1.31 |
| 51* | 484 | 568 | 0.85 |
| 52* | 262 | 239 | 1.10 |
| 53* | 965 | 968 | 1.00 |

> *Itens 51-53 presentes no arquivo — verificar se n=50 ou n=53 na leitura real.

**Observações dos dados:**
- Item 44: razão p/w = 48.5 (peso 2, valor 97) → quase sempre deve ser incluído
- Item 39: razão p/w = 2.13 (peso 15, valor 32) → boa inclusão
- Item 29: razão p/w = 0.19 (peso 101, valor 19) → candidato a exclusão
- Peso total de todos os itens: ~32.000 → capacidade 14.239 ≈ 44% dos itens (pelo peso)

---

## 10. Cronograma de Implementação

| Etapa | Descrição | Prioridade |
|-------|-----------|------------|
| 1 | Leitura dos dados e estrutura base do AG | Alta |
| 2 | Fitness com penalidade + operador de reparo | Alta |
| 3 | Seleção por torneio e roleta | Alta |
| 4 | Crossover 1 ponto e 2 pontos | Alta |
| 5 | Mutação bit-flip | Alta |
| 6 | Loop principal + elitismo | Alta |
| 7 | Experimentos: 7 configurações × 30 execuções | Média |
| 8 | Geração da tabela de resultados | Média |
| 9 | Análise e escrita do relatório | Alta |
