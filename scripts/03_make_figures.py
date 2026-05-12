from __future__ import annotations

import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from aic_openbim_acc.paths import DATA_PROCESSED, FIGURES, ensure_dirs


def save_workflow() -> None:
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.axis("off")
    steps = [
        "Regulatory text\nCODE-ACCORD",
        "Constrained rule\ncandidate extraction",
        "IDS-like intermediate\nrepresentation",
        "OpenBIM feature\nextraction",
        "Executable checks\nand evidence",
        "Counterfactual\nvalidation",
    ]
    x_positions = [0.04, 0.21, 0.39, 0.57, 0.74, 0.89]
    for i, (x, label) in enumerate(zip(x_positions, steps)):
        ax.text(
            x,
            0.55,
            label,
            ha="center",
            va="center",
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.45", facecolor="#eef3f7", edgecolor="#335c67"),
        )
        if i < len(steps) - 1:
            ax.annotate("", xy=(x_positions[i + 1] - 0.065, 0.55), xytext=(x + 0.065, 0.55), arrowprops=dict(arrowstyle="->", lw=1.6, color="#335c67"))
    ax.text(0.5, 0.08, "RuleBridge-BIM keeps generative AI outside the final verdict: all reported model decisions are produced by deterministic checks.", ha="center", fontsize=9)
    fig.savefig(FIGURES / "figure1_method_workflow.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_relation_bar() -> None:
    df = pd.read_csv(DATA_PROCESSED / "code_accord_relation_stats.csv")
    df = df.sort_values("n_relations", ascending=True)
    colors = df["machine_checkable_tier"].map({"direct_numeric": "#2a9d8f", "semantic_precondition": "#e9c46a", "not_direct": "#b8b8b8"})
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.barh(df["relation_type"], df["n_relations"], color=colors)
    ax.set_xlabel("Annotated relation pairs")
    ax.set_ylabel("")
    ax.set_title("Machine-checkability tiers in CODE-ACCORD relations")
    for y, value in enumerate(df["n_relations"]):
        ax.text(value + 12, y, str(value), va="center", fontsize=8)
    sns.despine(ax=ax)
    fig.savefig(FIGURES / "figure2_code_accord_relations.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_rule_heatmap() -> None:
    matrix = pd.read_csv(DATA_PROCESSED / "rule_results_model_level.csv")
    pivot = matrix.pivot_table(index="model", columns="rule_id", values="pass_rate", aggfunc="mean")
    pivot = pivot.loc[pivot.notna().sum(axis=1).sort_values(ascending=False).index]
    fig_height = max(5, 0.28 * len(pivot))
    fig, ax = plt.subplots(figsize=(9.5, fig_height))
    sns.heatmap(pivot, ax=ax, cmap="RdYlGn", vmin=0, vmax=1, cbar_kws={"label": "Pass rate"}, linewidths=0.25, linecolor="white")
    ax.set_xlabel("Executable rule")
    ax.set_ylabel("IFC model")
    ax.set_title("OpenBIM compliance-information pass rates across public IFC models")
    fig.savefig(FIGURES / "figure3_rule_pass_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_counterfactual() -> None:
    df = pd.read_csv(DATA_PROCESSED / "counterfactual_validation.csv")
    summary = df.groupby("rule_id", as_index=False).agg(
        neg=("negative_mutation_detection_rate", "mean"),
        repair=("positive_repair_success_rate", "mean"),
    )
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    x = range(len(summary))
    ax.bar([i - 0.18 for i in x], summary["neg"].fillna(0), width=0.36, label="Detect injected violation", color="#264653")
    ax.bar([i + 0.18 for i in x], summary["repair"].fillna(0), width=0.36, label="Accept synthetic repair", color="#f4a261")
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["rule_id"], rotation=45, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean validation rate")
    ax.set_title("Counterfactual validation of executable checks")
    ax.legend(frameon=False, loc="lower right")
    sns.despine(ax=ax)
    fig.savefig(FIGURES / "figure4_counterfactual_validation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_rule_theme_table_image() -> None:
    df = pd.read_csv(DATA_PROCESSED / "rule_results_model_level.csv")
    summary = (
        df.groupby(["theme"], as_index=False)
        .agg(target_count=("target_count", "sum"), fail_count=("fail_count", "sum"))
    )
    summary["fail_share"] = summary["fail_count"] / summary["target_count"].where(summary["target_count"] != 0)
    summary = summary.sort_values("fail_share", ascending=False)
    wrapped = [textwrap.fill(x, 24) for x in summary["theme"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.barh(wrapped, summary["fail_share"].fillna(0), color="#457b9d")
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Failure share across applicable objects")
    ax.set_title("Where public IFC models lose automated-checking readiness")
    sns.despine(ax=ax)
    fig.savefig(FIGURES / "figure5_failure_by_theme.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    sns.set_theme(style="whitegrid")
    save_workflow()
    save_relation_bar()
    save_rule_heatmap()
    save_counterfactual()
    save_rule_theme_table_image()


if __name__ == "__main__":
    main()

