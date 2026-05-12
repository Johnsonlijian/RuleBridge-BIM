from __future__ import annotations

from pathlib import Path

import ifcopenshell
import pandas as pd
import yaml

from aic_openbim_acc.ifc_rules import (
    applicable_objects,
    evaluate_feature,
    feature_from_object,
    make_feature_mutation,
)
from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, DATA_RAW, TABLES, ensure_dirs


INVENTORY_TYPES = [
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
    "IfcWall",
    "IfcDoor",
    "IfcWindow",
    "IfcSlab",
    "IfcBeam",
    "IfcColumn",
    "IfcStair",
    "IfcRailing",
    "IfcDistributionElement",
    "IfcBuildingElement",
]


def discover_ifc_files(config: dict) -> list[Path]:
    roots = [DATA_RAW / Path(config["paths"]["building_smart_ifc"]).name]
    files = []
    for root in roots:
        if root.exists():
            files.extend(sorted(root.rglob("*.ifc")))
    for item in config["paths"].get("extra_ifc", []):
        path = DATA_RAW / Path(item).name
        if path.exists():
            files.append(path)
    return files


def class_count(model: ifcopenshell.file, ifc_class: str) -> int:
    try:
        return len(model.by_type(ifc_class))
    except Exception:
        return 0


def model_label(path: Path) -> str:
    if path.name == "AdvancedProject.ifc":
        return "AdvancedProject"
    if "IFC 4.3.2.0" in str(path):
        return f"IFC4X3-{path.stem}"
    if "IFC 4.0.2.1" in str(path):
        return f"IFC4-{path.stem}"
    return path.stem


def main() -> None:
    ensure_dirs()
    config = yaml.safe_load((CONFIGS / "project.yml").read_text(encoding="utf-8"))
    rules = yaml.safe_load((CONFIGS / "rule_catalogue.yml").read_text(encoding="utf-8"))["rules"]
    max_examples = int(config["evaluation"]["max_failure_examples_per_rule"])

    inventory_rows = []
    element_rows = []
    rule_rows = []
    mutation_rows = []

    for path in discover_ifc_files(config):
        label = model_label(path)
        try:
            model = ifcopenshell.open(str(path))
        except Exception as exc:
            inventory_rows.append({"model": label, "path": str(path), "parse_status": "failed", "parse_error": str(exc)})
            continue

        inventory = {
            "model": label,
            "path": str(path),
            "schema": model.schema,
            "file_size_mb": round(path.stat().st_size / 1024 / 1024, 3),
            "parse_status": "ok",
            "parse_error": "",
        }
        for ifc_type in INVENTORY_TYPES:
            inventory[ifc_type] = class_count(model, ifc_type)
        inventory_rows.append(inventory)

        for rule in rules:
            targets = applicable_objects(model, rule["target_classes"])
            pass_count = 0
            fail_count = 0
            examples = []
            features = [feature_from_object(label, obj) for obj in targets]
            for feature in features:
                ok, reason = evaluate_feature(feature, rule)
                pass_count += int(ok)
                fail_count += int(not ok)
                element_rows.append(
                    {
                        "model": label,
                        "rule_id": rule["rule_id"],
                        "ifc_class": feature.ifc_class,
                        "global_id": feature.global_id,
                        "name": feature.name,
                        "passed": ok,
                        "reason": reason,
                    }
                )
                if not ok and len(examples) < max_examples:
                    examples.append(f"{feature.ifc_class}:{feature.global_id or feature.name or 'no-id'} ({reason})")

            target_count = len(features)
            pass_rate = pass_count / target_count if target_count else None
            rule_rows.append(
                {
                    "model": label,
                    "schema": model.schema,
                    "rule_id": rule["rule_id"],
                    "theme": rule["theme"],
                    "severity": rule["severity"],
                    "target_count": target_count,
                    "pass_count": pass_count,
                    "fail_count": fail_count,
                    "pass_rate": pass_rate,
                    "failure_examples": " | ".join(examples),
                }
            )

            sampled = features[:30]
            if sampled:
                fail_injections = 0
                repair_success = 0
                passable = 0
                repairable = 0
                for feature in sampled:
                    ok, _ = evaluate_feature(feature, rule)
                    if ok:
                        passable += 1
                        mutated = make_feature_mutation(feature, rule, should_pass=False)
                        mutated_ok, _ = evaluate_feature(mutated, rule)
                        fail_injections += int(not mutated_ok)
                    else:
                        repairable += 1
                        mutated = make_feature_mutation(feature, rule, should_pass=True)
                        mutated_ok, _ = evaluate_feature(mutated, rule)
                        repair_success += int(mutated_ok)
                mutation_rows.append(
                    {
                        "model": label,
                        "rule_id": rule["rule_id"],
                        "sampled_targets": len(sampled),
                        "negative_mutation_detection_rate": fail_injections / passable if passable else None,
                        "positive_repair_success_rate": repair_success / repairable if repairable else None,
                    }
                )

    inventory_df = pd.DataFrame(inventory_rows)
    element_df = pd.DataFrame(element_rows)
    rules_df = pd.DataFrame(rule_rows)
    mutation_df = pd.DataFrame(mutation_rows)

    inventory_df.to_csv(DATA_PROCESSED / "ifc_model_inventory.csv", index=False)
    element_df.to_csv(DATA_PROCESSED / "rule_results_element_level.csv", index=False)
    rules_df.to_csv(DATA_PROCESSED / "rule_results_model_level.csv", index=False)
    mutation_df.to_csv(DATA_PROCESSED / "counterfactual_validation.csv", index=False)

    inventory_df.to_csv(TABLES / "table1_model_inventory.csv", index=False)
    summary = (
        rules_df.groupby(["rule_id", "theme", "severity"], as_index=False)
        .agg(target_count=("target_count", "sum"), pass_count=("pass_count", "sum"), fail_count=("fail_count", "sum"))
    )
    summary["pass_rate"] = summary["pass_count"] / summary["target_count"].where(summary["target_count"] != 0)
    summary.to_csv(TABLES / "table2_rule_pass_rates.csv", index=False)
    matrix = rules_df.pivot_table(index="model", columns="rule_id", values="pass_rate", aggfunc="mean")
    matrix.to_csv(TABLES / "table3_model_rule_matrix.csv")
    mutation_df.to_csv(TABLES / "table4_counterfactual_validation.csv", index=False)


if __name__ == "__main__":
    main()

