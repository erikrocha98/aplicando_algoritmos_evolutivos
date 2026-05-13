"""
Gera os quatro gráficos de análise dos experimentos:
  1. Boxplot  — torneio k=3 vs roleta
  2. Heatmap  — pc × pm por tamanho de população
  3. Barras   — fitness médio por tamanho de população
  4. Convergência — melhor fitness por geração (mediana ± IQR)

Os três primeiros leem resultados_runs.csv.
O de convergência re-roda configs selecionadas para capturar o histórico.
"""

import os
import statistics

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from mochila_ag import GAConfig, load_data, run_ga

DATA_PATH  = "mochila.txt"
RUNS_CSV   = "resultados_runs.csv"
OUTPUT_DIR = "graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONVERGENCE_RUNS = 15   # execuções por config para o gráfico de convergência
MAX_GEN          = 500
STAGNATION       = 50


# ── helpers ──────────────────────────────────────────────────────────────────

def savefig(fig, name):
    path = os.path.join(OUTPUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Salvo: {path}")
    plt.close(fig)


# ── 1. Boxplot: torneio vs roleta ────────────────────────────────────────────

def plot_boxplot(df):
    torneio = df[df["selection"] == "tournament_k3"]["best_profit"]
    roleta  = df[df["selection"] == "roulette"]["best_profit"]

    fig, ax = plt.subplots(figsize=(7, 5))
    bp = ax.boxplot(
        [torneio, roleta],
        labels=["Torneio k=3", "Roleta"],
        patch_artist=True,
        medianprops=dict(color="black", linewidth=2),
    )
    colors = ["#4C72B0", "#DD8452"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_title("Distribuição do Melhor Lucro\nTorneio k=3 vs Roleta", fontsize=13)
    ax.set_ylabel("Melhor lucro (todas as configurações)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # anotações de mediana
    for i, data in enumerate([torneio, roleta], 1):
        med = statistics.median(data)
        ax.text(i, med + 5, f"{int(med):,}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    savefig(fig, "1_boxplot_torneio_vs_roleta.png")


# ── 2. Heatmap: pc × pm por tamanho de população ────────────────────────────

def plot_heatmap(df):
    pop_sizes = sorted(df["pop_size"].unique())
    pcs = sorted(df["pc"].unique())
    pms = sorted(df["pm"].unique())

    fig, axes = plt.subplots(1, len(pop_sizes), figsize=(14, 4), sharey=True)
    fig.suptitle("Fitness Médio — Heatmap pc × pm por Tamanho de População", fontsize=13)

    vmin = df.groupby(["pop_size", "pc", "pm"])["best_profit"].mean().min()
    vmax = df.groupby(["pop_size", "pc", "pm"])["best_profit"].mean().max()

    for ax, pop in zip(axes, pop_sizes):
        sub = df[df["pop_size"] == pop]
        matrix = (
            sub.groupby(["pc", "pm"])["best_profit"]
            .mean()
            .unstack("pm")
            .reindex(index=pcs, columns=pms)
        )
        im = ax.imshow(matrix.values, aspect="auto", cmap="YlOrRd",
                       vmin=vmin, vmax=vmax)

        ax.set_xticks(range(len(pms)))
        ax.set_xticklabels([str(p) for p in pms])
        ax.set_yticks(range(len(pcs)))
        ax.set_yticklabels([str(p) for p in pcs])
        ax.set_xlabel("pm")
        if ax is axes[0]:
            ax.set_ylabel("pc")
        ax.set_title(f"pop = {pop}")

        for r in range(len(pcs)):
            for c in range(len(pms)):
                val = matrix.values[r, c]
                ax.text(c, r, f"{val:.0f}", ha="center", va="center",
                        fontsize=8, color="black")

    fig.colorbar(im, ax=axes[-1], label="Lucro médio")
    savefig(fig, "2_heatmap_pc_pm_por_pop.png")


# ── 3. Barras: fitness médio por tamanho de população ───────────────────────

def plot_barras(df):
    pop_sizes = sorted(df["pop_size"].unique())
    sel_types = [("tournament_k3", "Torneio k=3"), ("roulette", "Roleta")]

    means = {label: [] for _, label in sel_types}
    stds  = {label: [] for _, label in sel_types}

    for pop in pop_sizes:
        for sel_key, label in sel_types:
            vals = df[(df["pop_size"] == pop) & (df["selection"] == sel_key)]["best_profit"]
            means[label].append(vals.mean())
            stds[label].append(vals.std())

    x = np.arange(len(pop_sizes))
    width = 0.35
    colors = ["#4C72B0", "#DD8452"]

    fig, ax = plt.subplots(figsize=(8, 5))
    for i, ((_, label), color) in enumerate(zip(sel_types, colors)):
        offset = (i - 0.5) * width
        bars = ax.bar(x + offset, means[label], width, label=label,
                      color=color, alpha=0.8,
                      yerr=stds[label], capsize=5, error_kw=dict(elinewidth=1.2))

    ax.set_title("Fitness Médio por Tamanho de População", fontsize=13)
    ax.set_xlabel("Tamanho de população")
    ax.set_ylabel("Lucro médio (30 execuções)")
    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in pop_sizes])
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # limitar eixo Y para ressaltar diferenças
    all_vals = [m for v in means.values() for m in v]
    ax.set_ylim(min(all_vals) * 0.99, max(all_vals) * 1.005)

    savefig(fig, "3_barras_fitness_por_pop.png")


# ── 4. Convergência por geração ──────────────────────────────────────────────

CONVERGENCE_CONFIGS = [
    ("Torneio pop=200 pc=0.9 pm=0.01 (melhor)", GAConfig(
        pop_size=200, pc=0.9, pm=0.01, selection="tournament", crossover="1pt",
        max_gen=MAX_GEN, stagnation_limit=STAGNATION, tournament_k=3,
    )),
    ("Torneio pop=50 pc=0.6 pm=0.01", GAConfig(
        pop_size=50, pc=0.6, pm=0.01, selection="tournament", crossover="1pt",
        max_gen=MAX_GEN, stagnation_limit=STAGNATION, tournament_k=3,
    )),
    ("Roleta pop=100 pc=0.8 pm=0.01 (melhor roleta)", GAConfig(
        pop_size=100, pc=0.8, pm=0.01, selection="roulette", crossover="1pt",
        max_gen=MAX_GEN, stagnation_limit=STAGNATION,
    )),
    ("Roleta pop=50 pc=0.9 pm=0.05 (pior)", GAConfig(
        pop_size=50, pc=0.9, pm=0.05, selection="roulette", crossover="1pt",
        max_gen=MAX_GEN, stagnation_limit=STAGNATION,
    )),
]


def pad_history(history, length):
    """Estende o histórico com o último valor até o comprimento desejado."""
    return history + [history[-1]] * (length - len(history))


def plot_convergencia(n, C, profits, weights):
    print(f"\nGerando histórico de convergência ({CONVERGENCE_RUNS} runs por config)...")
    colors = ["#4C72B0", "#55A868", "#DD8452", "#C44E52"]

    fig, ax = plt.subplots(figsize=(10, 6))

    for (label, cfg), color in zip(CONVERGENCE_CONFIGS, colors):
        print(f"  {label} ...", end=" ", flush=True)
        histories = []
        for _ in range(CONVERGENCE_RUNS):
            r = run_ga(cfg, n, C, profits, weights)
            histories.append(r.history)

        max_len = max(len(h) for h in histories)
        padded = np.array([pad_history(h, max_len) for h in histories])

        gens = np.arange(max_len)
        median = np.median(padded, axis=0)
        q25    = np.percentile(padded, 25, axis=0)
        q75    = np.percentile(padded, 75, axis=0)

        ax.plot(gens, median, label=label, color=color, linewidth=2)
        ax.fill_between(gens, q25, q75, color=color, alpha=0.15)
        print("ok")

    ax.set_title("Convergência por Geração\n(mediana ± IQR de 15 execuções)", fontsize=13)
    ax.set_xlabel("Geração")
    ax.set_ylabel("Melhor fitness acumulado")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=9)
    ax.grid(linestyle="--", alpha=0.4)

    savefig(fig, "4_convergencia_por_geracao.png")


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    df = pd.read_csv(RUNS_CSV)
    n, C, profits, weights = load_data(DATA_PATH)

    print("1. Boxplot torneio vs roleta...")
    plot_boxplot(df)

    print("2. Heatmap pc × pm por população...")
    plot_heatmap(df)

    print("3. Barras fitness médio por população...")
    plot_barras(df)

    print("4. Gráfico de convergência...")
    plot_convergencia(n, C, profits, weights)

    print(f"\nTodos os gráficos salvos em ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
