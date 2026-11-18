from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

REPORT_DIR = Path(__file__).resolve().parent
DATA_DIR = REPORT_DIR / "data"
FIGURES_DIR = REPORT_DIR / "figures"
EXAMPLE_SUPPORT = 2
COLORS = {
    "Exhaustive": "#2a78d6",
    "A-Priori (basic)": "#eb6834",
    "A-Priori (optimized)": "#1baf7a",
    "PCY (100,000 buckets)": "#eda100",
}
STYLE = {
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "legend.fontsize": 6.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": "#52514e",
    "xtick.color": "#898781",
    "ytick.color": "#898781",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e1e0d9",
    "grid.linewidth": 0.5,
    "lines.linewidth": 1.5,
    "lines.markersize": 3.5,
}


def pair_label(method):
    if method == "A-Priori (basic)":
        return f"{method}: candidate pairs"
    return f"{method}: pair counters"


def original_figure():
    runs = pd.read_csv(DATA_DIR / "original.csv")
    medians = runs.groupby(["method", "min_support"])["runtime_seconds"].median()
    pairs = runs.groupby(["method", "min_support"])["pair_counters"].first()

    fig, (runtime_ax, pairs_ax) = plt.subplots(1, 2, figsize=(6.5, 2.6))
    for method, color in COLORS.items():
        runtime_ax.plot(medians[method].index, medians[method].values, color=color, marker="o", label=method)
        if method != "Exhaustive":
            stored = pairs[method].where(pairs[method] > 0)
            pairs_ax.plot(stored.index, stored.values, color=color, marker="o", label=pair_label(method))

    supports = sorted(runs["min_support"].unique())
    runtime_ax.set(xlabel="support $s$ (movies)", ylabel="median time (s)", yscale="log", title="Runtime", xticks=supports)
    pairs_ax.set(xlabel="support $s$ (movies)", ylabel="pairs stored for pass 2", yscale="log", title="Pairs stored for pass 2", xticks=supports)
    for ax in (runtime_ax, pairs_ax):
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "original.pdf")
    return fig


def scaling_figure():
    panels = (
        ("plain_stacking.csv", "Plain stacking"),
        ("relabelled_stacking.csv", "Relabelled stacking"),
        ("relabelled_basic.csv", "Relabelled, basic A-Priori"),
    )
    fig, axes = plt.subplots(1, 3, figsize=(6.5, 2.6))
    for ax, (filename, title) in zip(axes, panels):
        runs = pd.read_csv(DATA_DIR / filename)
        runs = runs[runs["base_support"] == EXAMPLE_SUPPORT]
        medians = runs.groupby(["method", "movies"])["runtime_seconds"].median()
        for method, color in COLORS.items():
            if method in medians.index.get_level_values("method"):
                ax.plot(medians[method].index, medians[method].values, color=color, marker="o", label=method)
        ax.set(title=title, xlabel="baskets (thousands)", ylabel="median time (s)")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda value, position: f"{value / 1000:g}"))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(FIGURES_DIR / "scaling.pdf")
    return fig


def main():
    FIGURES_DIR.mkdir(exist_ok=True)
    plt.rcParams.update(STYLE)
    original_figure()
    scaling_figure()


if __name__ == "__main__":
    main()
