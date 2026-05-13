from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from aic_openbim_acc.paths import DATA_PROCESSED, FIGURES, ensure_dirs


def save_workflow() -> None:
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.axis("off")
    steps = [
        "Project delivery\ninformation need",
        "IDS-like evidence\nrequirement",
        "IFC evidence-route\nextraction",
        "RuleBridge / IDS\nreference comparison",
        "Evidence-route\ntriage",
        "BEP/EIR/RACI\naction",
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
    ax.text(0.5, 0.08, "RuleBridge-BIM separates missing evidence from non-compliance candidates before downstream checking.", ha="center", fontsize=9)
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
    matrix = pd.read_csv(DATA_PROCESSED / "readiness_by_corpus_stratum.csv")
    pivot = matrix.pivot_table(
        index="completeness_tier",
        columns="evidence_family",
        values="object_level_pass_rate",
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    sns.heatmap(pivot, ax=ax, cmap="RdYlGn", vmin=0, vmax=1, cbar_kws={"label": "Pass rate"}, linewidths=0.25, linecolor="white")
    ax.set_xlabel("Evidence family")
    ax.set_ylabel("Corpus stratum")
    ax.set_title("OpenBIM evidence readiness by public-corpus stratum")
    fig.savefig(FIGURES / "figure3_rule_pass_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_counterfactual() -> None:
    df = pd.read_csv(DATA_PROCESSED / "mutation_repair_operator_summary.csv")
    summary = df.pivot_table(index="rule_id", columns="original_state", values="success_rate", aggfunc="mean").reset_index()
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    x = range(len(summary))
    ax.bar([i - 0.18 for i in x], summary.get("pass", pd.Series([0] * len(summary))).fillna(0), width=0.36, label="Detect removed evidence", color="#264653")
    ax.bar([i + 0.18 for i in x], summary.get("fail", pd.Series([0] * len(summary))).fillna(0), width=0.36, label="Recover synthetic repair", color="#f4a261")
    ax.set_xticks(list(x))
    ax.set_xticklabels(summary["rule_id"], rotation=45, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Mean validation rate")
    ax.set_title("Evidence-mutation and repair sensitivity")
    ax.legend(frameon=False, loc="lower right")
    sns.despine(ax=ax)
    fig.savefig(FIGURES / "figure4_counterfactual_validation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_rule_theme_table_image() -> None:
    df = pd.read_csv(DATA_PROCESSED / "evidence_route_element_level.csv")
    total = df.groupby("evidence_family", as_index=False).size().rename(columns={"size": "target_count"})
    fail = (
        df[df["triage_state"] != "ready"]
        .groupby("evidence_family", as_index=False)
        .size()
        .rename(columns={"size": "fail_count"})
    )
    summary = total.merge(fail, on="evidence_family", how="left").fillna({"fail_count": 0})
    summary["fail_share"] = summary["fail_count"] / summary["target_count"].where(summary["target_count"] != 0)
    summary = summary.sort_values("fail_share", ascending=False)
    wrapped = [textwrap.fill(x.replace("_", " "), 24) for x in summary["evidence_family"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.barh(wrapped, summary["fail_share"].fillna(0), color="#457b9d")
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Failure share across applicable objects")
    ax.set_title("Evidence gaps by delivery evidence family")
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
