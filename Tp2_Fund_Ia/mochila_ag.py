import random
import statistics
from dataclasses import dataclass
from typing import List, Tuple


# ── Dados ────────────────────────────────────────────────────────────────────

def load_data(path: str) -> Tuple[int, int, List[int], List[int]]:
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    n = int(lines[0])
    C = int(lines[1])
    profits, weights = [], []
    for line in lines[2 : 2 + n]:
        p, w = map(int, line.split())
        profits.append(p)
        weights.append(w)
    return n, C, profits, weights


# ── População ────────────────────────────────────────────────────────────────

def init_population(pop_size: int, n: int) -> List[List[int]]:
    return [[random.randint(0, 1) for _ in range(n)] for _ in range(pop_size)]


# ── Fitness e Reparo ─────────────────────────────────────────────────────────

def fitness(
    individual: List[int],
    profits: List[int],
    weights: List[int],
    C: int,
    alpha: float,
) -> float:
    total_profit = sum(p * x for p, x in zip(profits, individual))
    total_weight = sum(w * x for w, x in zip(weights, individual))
    excess = max(0, total_weight - C)
    return total_profit - alpha * excess


def repair(
    individual: List[int],
    profits: List[int],
    weights: List[int],
    C: int,
) -> List[int]:
    """Remove itens com pior razão p/w até respeitar a capacidade."""
    ind = individual[:]
    total_weight = sum(w * x for w, x in zip(weights, ind))
    if total_weight <= C:
        return ind
    # ordena os itens selecionados pela razão p/w crescente (piores primeiro)
    selected = sorted(
        [i for i in range(len(ind)) if ind[i] == 1],
        key=lambda i: profits[i] / weights[i],
    )
    for i in selected:
        if total_weight <= C:
            break
        ind[i] = 0
        total_weight -= weights[i]
    return ind


def eval_population(
    population: List[List[int]],
    profits: List[int],
    weights: List[int],
    C: int,
    alpha: float,
    use_repair: bool,
) -> Tuple[List[List[int]], List[float]]:
    if use_repair:
        population = [repair(ind, profits, weights, C) for ind in population]
    fits = [fitness(ind, profits, weights, C, alpha) for ind in population]
    return population, fits


# ── Seleção ──────────────────────────────────────────────────────────────────

def select_tournament(
    population: List[List[int]], fitnesses: List[float], k: int = 2
) -> List[int]:
    candidates = random.sample(range(len(population)), k)
    best = max(candidates, key=lambda i: fitnesses[i])
    return population[best][:]


def select_roulette(
    population: List[List[int]], fitnesses: List[float]
) -> List[int]:
    min_f = min(fitnesses)
    # desloca para garantir valores positivos
    shifted = [f - min_f + 1e-6 for f in fitnesses]
    total = sum(shifted)
    pick = random.uniform(0, total)
    cumulative = 0.0
    for i, f in enumerate(shifted):
        cumulative += f
        if cumulative >= pick:
            return population[i][:]
    return population[-1][:]


# ── Cruzamento ───────────────────────────────────────────────────────────────

def crossover_1pt(
    p1: List[int], p2: List[int], pc: float
) -> Tuple[List[int], List[int]]:
    if random.random() > pc:
        return p1[:], p2[:]
    pt = random.randint(1, len(p1) - 1)
    return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]


def crossover_2pt(
    p1: List[int], p2: List[int], pc: float
) -> Tuple[List[int], List[int]]:
    if random.random() > pc:
        return p1[:], p2[:]
    pt1, pt2 = sorted(random.sample(range(1, len(p1)), 2))
    c1 = p1[:pt1] + p2[pt1:pt2] + p1[pt2:]
    c2 = p2[:pt1] + p1[pt1:pt2] + p2[pt2:]
    return c1, c2


# ── Mutação ──────────────────────────────────────────────────────────────────

def mutate(individual: List[int], pm: float) -> List[int]:
    return [1 - gene if random.random() < pm else gene for gene in individual]


# ── Configuração e Resultado ─────────────────────────────────────────────────

@dataclass
class GAConfig:
    pop_size: int
    pc: float
    pm: float
    selection: str       # 'tournament' | 'roulette'
    crossover: str       # '1pt' | '2pt'
    max_gen: int = 500
    stagnation_limit: int = 50
    tournament_k: int = 2
    use_repair: bool = False
    label: str = ""


@dataclass
class GAResult:
    best_fitness: float
    best_individual: List[int]
    generations: int
    best_weight: int
    best_profit: int
    history: List[float] = None  # melhor fitness por geração


# ── Loop Principal do AG ─────────────────────────────────────────────────────

def run_ga(
    config: GAConfig,
    n: int,
    C: int,
    profits: List[int],
    weights: List[int],
) -> GAResult:
    # alpha garante que qualquer solução inválida seja pior que qualquer válida
    alpha = max(p / w for p, w in zip(profits, weights)) * 2

    population = init_population(config.pop_size, n)
    population, fitnesses = eval_population(
        population, profits, weights, C, alpha, config.use_repair
    )

    best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
    best_individual = population[best_idx][:]
    best_fitness = fitnesses[best_idx]
    stagnation = 0
    history = [best_fitness]

    for gen in range(1, config.max_gen + 1):
        new_pop = [best_individual[:]]  # elitismo: preserva o melhor

        while len(new_pop) < config.pop_size:
            if config.selection == "tournament":
                p1 = select_tournament(population, fitnesses, config.tournament_k)
                p2 = select_tournament(population, fitnesses, config.tournament_k)
            else:
                p1 = select_roulette(population, fitnesses)
                p2 = select_roulette(population, fitnesses)

            if config.crossover == "1pt":
                c1, c2 = crossover_1pt(p1, p2, config.pc)
            else:
                c1, c2 = crossover_2pt(p1, p2, config.pc)

            c1 = mutate(c1, config.pm)
            c2 = mutate(c2, config.pm)
            new_pop.extend([c1, c2])

        population = new_pop[: config.pop_size]
        population, fitnesses = eval_population(
            population, profits, weights, C, alpha, config.use_repair
        )

        gen_best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_individual = population[gen_best_idx][:]
            stagnation = 0
        else:
            stagnation += 1

        history.append(best_fitness)

        if stagnation >= config.stagnation_limit:
            break

    best_weight = sum(w * x for w, x in zip(weights, best_individual))
    best_profit = sum(p * x for p, x in zip(profits, best_individual))
    return GAResult(
        best_fitness=best_fitness,
        best_individual=best_individual,
        generations=gen,
        best_weight=best_weight,
        best_profit=best_profit,
        history=history,
    )


# ── Experimentos ─────────────────────────────────────────────────────────────

CONFIGS = [
    GAConfig(pop_size=50,  pc=0.8, pm=0.01, selection="tournament", crossover="1pt", label="A"),
    GAConfig(pop_size=50,  pc=0.8, pm=0.05, selection="tournament", crossover="1pt", label="B"),
    GAConfig(pop_size=100, pc=0.8, pm=0.01, selection="tournament", crossover="1pt", label="C"),
    GAConfig(pop_size=100, pc=0.9, pm=0.01, selection="tournament", crossover="2pt", label="D"),
    GAConfig(pop_size=100, pc=0.8, pm=0.01, selection="roulette",   crossover="1pt", label="E"),
    GAConfig(pop_size=200, pc=0.8, pm=0.01, selection="tournament", crossover="1pt", label="F"),
    GAConfig(pop_size=100, pc=0.6, pm=0.02, selection="tournament", crossover="2pt", label="G"),
]

RUNS = 30


def run_experiments(n: int, C: int, profits: List[int], weights: List[int]) -> None:
    header = (
        f"\n{'Cfg':<4} {'Pop':>5} {'pc':>5} {'pm':>6} {'Seleção':>10} {'Cross':>5} "
        f"{'Fit Média':>12} {'Fit DP':>10} {'Gen Média':>10} {'Gen DP':>8} {'Melhor Lucro':>13}"
    )
    print(header)
    print("-" * len(header))

    for cfg in CONFIGS:
        results = [run_ga(cfg, n, C, profits, weights) for _ in range(RUNS)]
        fits   = [r.best_fitness for r in results]
        gens   = [r.generations  for r in results]
        best_r = max(results, key=lambda r: r.best_profit)

        print(
            f"{cfg.label:<4} {cfg.pop_size:>5} {cfg.pc:>5.1f} {cfg.pm:>6.3f} "
            f"{cfg.selection:>10} {cfg.crossover:>5} "
            f"{statistics.mean(fits):>12.2f} {statistics.stdev(fits):>10.2f} "
            f"{statistics.mean(gens):>10.1f} {statistics.stdev(gens):>8.1f} "
            f"{best_r.best_profit:>13}"
        )


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    n, C, profits, weights = load_data("mochila.txt")
    print(f"Instância carregada: n={n}, C={C}")
    print(f"Soma dos pesos: {sum(weights)}, Soma dos valores: {sum(profits)}")
    print(f"Executando {RUNS} rodadas por configuração ({len(CONFIGS)} configs)...")
    run_experiments(n, C, profits, weights)


if __name__ == "__main__":
    main()
