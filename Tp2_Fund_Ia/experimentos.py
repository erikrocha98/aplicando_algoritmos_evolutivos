"""
Bateria de experimentos sistemáticos para o AG da mochila.

Grade:
  pop_size  : 50, 100, 200
  pc        : 0.6, 0.8, 0.9
  pm        : 0.01, 0.03, 0.05
  selection : tournament_k3, roulette

Crossover fixado em 1 ponto (padrão do trabalho).
30 execuções independentes por configuração.
Resultados salvos em:
  resultados_runs.csv    — uma linha por execução
  resultados_resumo.csv  — média/dp por configuração
"""

import csv
import itertools
import statistics
import time

from mochila_ag import GAConfig, GAResult, load_data, run_ga

DATA_PATH = "mochila.txt"
RUNS = 30
CROSSOVER = "1pt"
MAX_GEN = 500
STAGNATION = 50

POP_SIZES  = [50, 100, 200]
PCS        = [0.6, 0.8, 0.9]
PMS        = [0.01, 0.03, 0.05]
SELECTIONS = [
    ("tournament_k3", "tournament", 3),
    ("roulette",      "roulette",   2),
]

RUNS_FILE    = "resultados_runs.csv"
SUMMARY_FILE = "resultados_resumo.csv"

RUNS_HEADER = [
    "config_id", "pop_size", "pc", "pm", "selection",
    "run", "best_fitness", "best_profit", "best_weight", "generations",
]
SUMMARY_HEADER = [
    "config_id", "pop_size", "pc", "pm", "selection",
    "fit_media", "fit_dp", "profit_media", "profit_dp",
    "gen_media", "gen_dp", "melhor_profit_global",
]


def make_configs():
    configs = []
    for (sel_label, sel_type, k), pop, pc, pm in itertools.product(
        SELECTIONS, POP_SIZES, PCS, PMS
    ):
        cfg_id = f"pop{pop}_pc{pc}_pm{pm}_{sel_label}"
        cfg = GAConfig(
            pop_size=pop,
            pc=pc,
            pm=pm,
            selection=sel_type,
            crossover=CROSSOVER,
            max_gen=MAX_GEN,
            stagnation_limit=STAGNATION,
            tournament_k=k,
            label=cfg_id,
        )
        configs.append((cfg_id, sel_label, cfg))
    return configs


def estimate_time(n, C, profits, weights, configs):
    cfg_id, sel_label, cfg = configs[0]
    t0 = time.time()
    run_ga(cfg, n, C, profits, weights)
    elapsed = time.time() - t0
    total = elapsed * RUNS * len(configs)
    print(f"  1 execucao ~ {elapsed:.2f}s  =>  estimativa total: {total/60:.1f} min")


def run_all(n, C, profits, weights, configs):
    runs_rows = []
    summary_rows = []
    total = len(configs)

    for idx, (cfg_id, sel_label, cfg) in enumerate(configs, 1):
        print(f"[{idx:>3}/{total}] {cfg_id} ...", end=" ", flush=True)
        t0 = time.time()

        results: list[GAResult] = [
            run_ga(cfg, n, C, profits, weights) for _ in range(RUNS)
        ]

        for run_i, r in enumerate(results, 1):
            runs_rows.append([
                cfg_id, cfg.pop_size, cfg.pc, cfg.pm, sel_label,
                run_i, r.best_fitness, r.best_profit, r.best_weight, r.generations,
            ])

        fits    = [r.best_fitness for r in results]
        profits_ = [r.best_profit  for r in results]
        gens    = [r.generations   for r in results]
        best_profit_global = max(profits_)

        summary_rows.append([
            cfg_id, cfg.pop_size, cfg.pc, cfg.pm, sel_label,
            round(statistics.mean(fits),    2),
            round(statistics.stdev(fits),   2),
            round(statistics.mean(profits_), 2),
            round(statistics.stdev(profits_), 2),
            round(statistics.mean(gens),    2),
            round(statistics.stdev(gens),   2),
            best_profit_global,
        ])

        print(f"ok ({time.time()-t0:.1f}s)  melhor lucro={best_profit_global}")

    return runs_rows, summary_rows


def save_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"Salvo: {path}  ({len(rows)} linhas)")


def main():
    n, C, profits, weights = load_data(DATA_PATH)
    print(f"Instancia: n={n}, C={C}")

    configs = make_configs()
    print(f"Total de configuracoes: {len(configs)}  |  execucoes por config: {RUNS}")
    print(f"Total de runs: {len(configs) * RUNS}\n")

    print("Estimando tempo...")
    estimate_time(n, C, profits, weights, configs)
    print()

    runs_rows, summary_rows = run_all(n, C, profits, weights, configs)

    save_csv(RUNS_FILE,    RUNS_HEADER,    runs_rows)
    save_csv(SUMMARY_FILE, SUMMARY_HEADER, summary_rows)

    # top 5 configuracoes por melhor lucro global
    summary_rows.sort(key=lambda r: r[-1], reverse=True)
    print("\nTop 5 configuracoes (melhor lucro global):")
    print(f"{'Config':<45} {'Lucro':>7} {'Fit media':>10} {'Fit DP':>8} {'Gen media':>9}")
    for row in summary_rows[:5]:
        cfg_id, pop, pc, pm, sel, fit_m, fit_dp, pr_m, pr_dp, gen_m, gen_dp, best = row
        print(f"{cfg_id:<45} {best:>7}  {fit_m:>10.2f}  {fit_dp:>8.2f}  {gen_m:>9.2f}")


if __name__ == "__main__":
    main()
