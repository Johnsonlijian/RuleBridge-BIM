from __future__ import annotations

import numpy as np
import pandas as pd

from aic_openbim_acc.paths import DATA_PROCESSED, TABLES, ensure_dirs


RULE_FAMILY = {
    "R01_GLOBAL_ID": "information_continuity",
    "R02_OBJECT_NAME": "information_continuity",
    "R03_TYPE_OR_OBJECTTYPE": "semantic_definition",
    "R04_SPATIAL_CONTAINMENT": "spatial_project_context",
    "R05_MATERIAL_AVAILABLE": "material_product_evidence",
    "R06_DOOR_CLEAR_WIDTH": "regulatory_attributes",
    "R07_WINDOW_DIMENSIONS": "regulatory_attributes",
    "R08_SPACE_AREA": "regulatory_attributes",
    "R09_FIRE_RATING": "regulatory_attributes",
    "R10_SITE_GEOREFERENCE": "spatial_project_context",
}


def _iqr(values: pd.Series) -> str:
    clean = values.dropna()
    if clean.empty:
        return ""
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    return f"{q1:.3f}-{q3:.3f}"


def grouped_readiness(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows = []
    valid = df[df["target_count"] > 0].copy()
    for keys, g in valid.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        target = int(g["target_count"].sum())
        passed = int(g["pass_count"].sum())
        failed = int(g["fail_count"].sum())
        row = dict(zip(group_cols, keys))
        row.update(
            {
                "models_with_targets": int(g["model"].nunique()),
                "object_rule_targets": target,
                "pass_count": passed,
                "fail_count": failed,
                "object_level_pass_rate": passed / target if target else np.nan,
                "model_level_median_pass_rate": g["pass_rate"].median(),
                "model_level_iqr": _iqr(g["pass_rate"]),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def model_readiness(df: pd.DataFrame) -> pd.DataFrame:
    valid = df[df["target_count"] > 0].copy()
    overall = (
        valid.groupby(["model", "source_repository", "schema", "model_type", "completeness_tier"], as_index=False)
        .agg(
            applicable_rules=("rule_id", "nunique"),
            target_count=("target_count", "sum"),
            pass_count=("pass_count", "sum"),
        )
    )
    overall["model_readiness_index"] = overall["pass_count"] / overall["target_count"].where(overall["target_count"] != 0)
    return overall


def bootstrap_intervals(df: pd.DataFrame, iterations: int = 500, seed: int = 20260513) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    valid = df[df["target_count"] > 0].copy()
    rows = []
    for (tier, family), g in valid.groupby(["completeness_tier", "evidence_family"], dropna=False):
        per_model = (
            g.groupby("model", as_index=False)
            .agg(target_count=("target_count", "sum"), pass_count=("pass_count", "sum"))
            .query("target_count > 0")
        )
        if per_model.empty:
            continue
        target_arr = per_model["target_count"].to_numpy(dtype=float)
        pass_arr = per_model["pass_count"].to_numpy(dtype=float)
        rates = []
        for _ in range(iterations):
            idx = rng.integers(0, len(per_model), size=len(per_model))
            target = target_arr[idx].sum()
            rates.append(pass_arr[idx].sum() / target if target else np.nan)
        clean = np.array([r for r in rates if not np.isnan(r)])
        if clean.size == 0:
            continue
        target = int(g["target_count"].sum())
        rows.append(
            {
                "completeness_tier": tier,
                "evidence_family": family,
                "models_with_targets": int(len(per_model)),
                "object_rule_targets": target,
                "observed_pass_rate": float(g["pass_count"].sum() / target) if target else np.nan,
                "bootstrap_p05": float(np.quantile(clean, 0.05)),
                "bootstrap_p50": float(np.quantile(clean, 0.50)),
                "bootstrap_p95": float(np.quantile(clean, 0.95)),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ensure_dirs()
    inv = pd.read_csv(DATA_PROCESSED / "ifc_model_inventory.csv")
    rules = pd.read_csv(DATA_PROCESSED / "rule_results_model_level.csv")
    rules["evidence_family"] = rules["rule_id"].map(RULE_FAMILY).fillna("other")

    corpus = (
        inv.groupby(["source_repository", "schema", "model_type", "completeness_tier", "parse_status"], dropna=False)
        .size()
        .reset_index(name="model_count")
        .sort_values(["source_repository", "schema", "model_type", "completeness_tier", "parse_status"])
    )
    corpus.to_csv(DATA_PROCESSED / "corpus_manifest_strata.csv", index=False)

    by_tier_family = grouped_readiness(rules, ["completeness_tier", "evidence_family"])
    by_source_schema = grouped_readiness(rules, ["source_repository", "schema", "evidence_family"])
    by_rule_tier = grouped_readiness(rules, ["rule_id", "completeness_tier"])
    readiness = model_readiness(rules)
    intervals = bootstrap_intervals(rules)

    by_tier_family.to_csv(DATA_PROCESSED / "readiness_by_corpus_stratum.csv", index=False)
    by_source_schema.to_csv(DATA_PROCESSED / "readiness_by_source_schema.csv", index=False)
    by_rule_tier.to_csv(DATA_PROCESSED / "readiness_by_rule_and_tier.csv", index=False)
    readiness.to_csv(DATA_PROCESSED / "model_readiness_index.csv", index=False)
    intervals.to_csv(DATA_PROCESSED / "cluster_bootstrap_intervals.csv", index=False)

    by_tier_family.to_csv(TABLES / "table5_expanded_corpus_strata.csv", index=False)
    intervals.to_csv(TABLES / "table6_cluster_bootstrap_intervals.csv", index=False)
    corpus.to_csv(TABLES / "table_s1_corpus_manifest_strata.csv", index=False)
    by_source_schema.to_csv(TABLES / "table_s2_source_schema_readiness.csv", index=False)


if __name__ == "__main__":
    main()
