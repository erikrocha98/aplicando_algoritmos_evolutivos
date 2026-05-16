"""Evolucao Diferencial para minimizar a funcao esfera em 10 dimensoes.

Variante implementada: DE/rand/1/bin.
Uso principal:
    python3 ed_esfera.py test
    python3 ed_esfera.py demo
    python3 ed_esfera.py experiment --output resultados_ed.csv
"""

from __future__ import annotations

import argparse
import csv
import random
import statistics
from dataclasses import dataclass
from itertools import product
from typing import Iterable, Sequence


DIMENSIONS = 10
LOWER_BOUND = -5.0
UPPER_BOUND = 5.0
FITNESS_TARGET = 1e-6
MAX_GENERATIONS = 1000


@dataclass(frozen=True)
class DEResult:
    best_vector: list[float]
    best_fitness: float
    generations: int
    converged: bool
    history: list[float]


def sphere(vector: Sequence[float]) -> float:
    """Funcao objetivo f(x) = sum(x_i^2)."""
    return sum(value * value for value in vector)


def clip(value: float, lower: float = LOWER_BOUND, upper: float = UPPER_BOUND) -> float:
    if value < lower:
        return lower
    if value > upper:
        return upper
    return value


def initialize_population(
    population_size: int,
    dimensions: int,
    rng: random.Random,
    lower: float = LOWER_BOUND,
    upper: float = UPPER_BOUND,
) -> list[list[float]]:
    validate_population_size(population_size)
    if dimensions <= 0:
        raise ValueError("dimensions must be positive")

    return [
        [rng.uniform(lower, upper) for _ in range(dimensions)]
        for _ in range(population_size)
    ]


def validate_population_size(population_size: int) -> None:
    if population_size < 4:
        raise ValueError("population_size must be at least 4 for DE/rand/1")


def validate_parameters(scale_factor: float, crossover_rate: float) -> None:
    if scale_factor < 0:
        raise ValueError("scale_factor must be non-negative")
    if not 0 <= crossover_rate <= 1:
        raise ValueError("crossover_rate must be between 0 and 1")


def differential_mutation(
    population: Sequence[Sequence[float]],
    target_index: int,
    scale_factor: float,
    rng: random.Random,
    lower: float = LOWER_BOUND,
    upper: float = UPPER_BOUND,
) -> list[float]:
    """Gera o vetor mutante v = x_r1 + F * (x_r2 - x_r3)."""
    validate_population_size(len(population))
    candidates = [index for index in range(len(population)) if index != target_index]
    r1, r2, r3 = rng.sample(candidates, 3)

    base = population[r1]
    diff_a = population[r2]
    diff_b = population[r3]

    return [
        clip(base[j] + scale_factor * (diff_a[j] - diff_b[j]), lower, upper)
        for j in range(len(base))
    ]


def binomial_crossover(
    target: Sequence[float],
    mutant: Sequence[float],
    crossover_rate: float,
    rng: random.Random,
) -> list[float]:
    """Recombinacao binomial garantindo ao menos um gene do mutante."""
    if len(target) != len(mutant):
        raise ValueError("target and mutant must have the same length")
    if len(target) == 0:
        raise ValueError("vectors must not be empty")
    validate_parameters(scale_factor=0.0, crossover_rate=crossover_rate)

    forced_gene = rng.randrange(len(target))
    trial = []
    for j, target_gene in enumerate(target):
        if j == forced_gene or rng.random() < crossover_rate:
            trial.append(mutant[j])
        else:
            trial.append(target_gene)
    return trial


def elitist_selection(
    target: Sequence[float],
    target_fitness: float,
    trial: Sequence[float],
    trial_fitness: float,
) -> tuple[list[float], float]:
    """Retorna o individuo que segue para a proxima geracao."""
    if trial_fitness <= target_fitness:
        return list(trial), trial_fitness
    return list(target), target_fitness


def differential_evolution(
    population_size: int,
    scale_factor: float,
    crossover_rate: float,
    *,
    dimensions: int = DIMENSIONS,
    lower: float = LOWER_BOUND,
    upper: float = UPPER_BOUND,
    max_generations: int = MAX_GENERATIONS,
    fitness_target: float = FITNESS_TARGET,
    seed: int | None = None,
    keep_history: bool = True,
) -> DEResult:
    """Executa DE/rand/1/bin para minimizar a funcao esfera."""
    validate_population_size(population_size)
    validate_parameters(scale_factor, crossover_rate)
    if max_generations < 0:
        raise ValueError("max_generations must be non-negative")

    rng = random.Random(seed)
    population = initialize_population(population_size, dimensions, rng, lower, upper)
    fitnesses = [sphere(individual) for individual in population]

    best_index = min(range(population_size), key=fitnesses.__getitem__)
    best_vector = list(population[best_index])
    best_fitness = fitnesses[best_index]
    history = [best_fitness] if keep_history else []

    if best_fitness <= fitness_target:
        return DEResult(best_vector, best_fitness, 0, True, history)

    generations = 0
    for generation in range(1, max_generations + 1):
        next_population: list[list[float]] = []
        next_fitnesses: list[float] = []

        # A mutacao usa a populacao da geracao corrente, nao a parcialmente atualizada.
        for target_index, target in enumerate(population):
            mutant = differential_mutation(
                population,
                target_index,
                scale_factor,
                rng,
                lower,
                upper,
            )
            trial = binomial_crossover(target, mutant, crossover_rate, rng)
            trial_fitness = sphere(trial)
            selected, selected_fitness = elitist_selection(
                target,
                fitnesses[target_index],
                trial,
                trial_fitness,
            )
            next_population.append(selected)
            next_fitnesses.append(selected_fitness)

        population = next_population
        fitnesses = next_fitnesses
        generations = generation

        generation_best_index = min(range(population_size), key=fitnesses.__getitem__)
        generation_best_fitness = fitnesses[generation_best_index]
        if generation_best_fitness < best_fitness:
            best_fitness = generation_best_fitness
            best_vector = list(population[generation_best_index])

        if keep_history:
            history.append(best_fitness)

        if best_fitness <= fitness_target:
            return DEResult(best_vector, best_fitness, generations, True, history)

    return DEResult(best_vector, best_fitness, generations, False, history)


def summarize_runs(results: Sequence[DEResult], max_generations: int) -> dict[str, float | int]:
    best_fitnesses = [result.best_fitness for result in results]
    generations = [result.generations if result.converged else max_generations for result in results]
    success_count = sum(1 for result in results if result.converged)

    return {
        "best_fitness_mean": statistics.mean(best_fitnesses),
        "best_fitness_std": statistics.stdev(best_fitnesses) if len(best_fitnesses) > 1 else 0.0,
        "generations_mean": statistics.mean(generations),
        "generations_std": statistics.stdev(generations) if len(generations) > 1 else 0.0,
        "success_rate": success_count / len(results),
        "success_count": success_count,
    }


def run_experiment_grid(
    population_sizes: Iterable[int],
    scale_factors: Iterable[float],
    crossover_rates: Iterable[float],
    *,
    repetitions: int = 30,
    max_generations: int = MAX_GENERATIONS,
    fitness_target: float = FITNESS_TARGET,
    base_seed: int = 20240511,
    progress: bool = False,
) -> list[dict[str, float | int]]:
    if repetitions <= 0:
        raise ValueError("repetitions must be positive")

    rows: list[dict[str, float | int]] = []
    configurations = list(product(population_sizes, scale_factors, crossover_rates))

    for config_index, (population_size, scale_factor, crossover_rate) in enumerate(configurations):
        if progress:
            print(
                "running "
                f"pop={population_size}, F={scale_factor}, CR={crossover_rate} "
                f"({config_index + 1}/{len(configurations)})",
                flush=True,
            )

        results = [
            differential_evolution(
                population_size,
                scale_factor,
                crossover_rate,
                max_generations=max_generations,
                fitness_target=fitness_target,
                seed=base_seed + config_index * repetitions + repetition,
                keep_history=False,
            )
            for repetition in range(repetitions)
        ]
        summary = summarize_runs(results, max_generations)

        rows.append(
            {
                "population_size": population_size,
                "scale_factor_F": scale_factor,
                "crossover_rate_CR": crossover_rate,
                "repetitions": repetitions,
                "max_generations": max_generations,
                "fitness_target": fitness_target,
                **summary,
            }
        )

    return rows


def write_csv(rows: Sequence[dict[str, float | int]], output_path: str) -> None:
    if not rows:
        raise ValueError("rows must not be empty")

    fieldnames = list(rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_self_tests() -> None:
    import unittest

    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_ed_esfera.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evolucao Diferencial DE/rand/1/bin para a funcao esfera."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("demo", help="executa uma rodada curta de exemplo")
    demo.add_argument("--population-size", type=int, default=20)
    demo.add_argument("--scale-factor", type=float, default=0.5)
    demo.add_argument("--crossover-rate", type=float, default=0.7)
    demo.add_argument("--max-generations", type=int, default=MAX_GENERATIONS)
    demo.add_argument("--seed", type=int, default=20240511)

    experiment = subparsers.add_parser("experiment", help="gera a tabela CSV de experimentos")
    experiment.add_argument("--output", default="resultados_ed.csv")
    experiment.add_argument("--repetitions", type=int, default=30)
    experiment.add_argument("--max-generations", type=int, default=MAX_GENERATIONS)
    experiment.add_argument("--seed", type=int, default=20240511)
    experiment.add_argument("--progress", action="store_true")

    subparsers.add_parser("test", help="executa os testes automatizados")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "test":
        run_self_tests()
        return

    if args.command == "demo":
        result = differential_evolution(
            args.population_size,
            args.scale_factor,
            args.crossover_rate,
            max_generations=args.max_generations,
            seed=args.seed,
        )
        print(f"best_fitness={result.best_fitness:.12g}")
        print(f"generations={result.generations}")
        print(f"converged={result.converged}")
        print("best_vector=[" + ", ".join(f"{value:.6g}" for value in result.best_vector) + "]")
        return

    if args.command == "experiment":
        rows = run_experiment_grid(
            population_sizes=(20, 50, 100),
            scale_factors=(0.3, 0.5, 0.8),
            crossover_rates=(0.3, 0.7, 0.9),
            repetitions=args.repetitions,
            max_generations=args.max_generations,
            base_seed=args.seed,
            progress=args.progress,
        )
        write_csv(rows, args.output)
        print(f"wrote {len(rows)} rows to {args.output}")
        return

    parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
