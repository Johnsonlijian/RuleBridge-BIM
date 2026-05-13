from __future__ import annotations

from typing import Any

import ifcopenshell
import pandas as pd
import yaml

from aic_openbim_acc.corpus import discover_ifc_files, inventory_row
from aic_openbim_acc.ifc_rules import applicable_objects, evaluate_feature, feature_from_object, make_feature_mutation
from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, TABLES, ensure_dirs


NEGATIVE_OPERATOR = {
    "required_attribute": "remove_required_attribute",
    "type_or_object_type": "remove_type_routes",
    "containment_required": "break_spatial_containment",
    "material_assigned": "remove_material_assignment",
    "numeric_attribute_min": "lower_numeric_attribute_below_threshold",
    "numeric_attributes_positive": "remove_positive_dimensions",
    "property_any_positive": "remove_area_properties",
    "fire_rating_available": "remove_fire_rating_evidence",
    "site_georeferenced": "remove_site_georeference",
}

POSITIVE_OPERATOR = {
    "required_attribute": "repair_required_attribute",
    "type_or_object_type": "repair_type_route",
    "containment_required": "repair_spatial_containment_flag",
    "material_assigned": "repair_material_assignment_flag",
    "numeric_attribute_min": "repair_numeric_attribute_to_threshold",
    "numeric_attributes_positive": "repair_positive_dimensions",
    "property_any_positive": "repair_area_property",
    "fire_rating_available": "repair_fire_rating_property",
    "site_georeferenced": "repair_site_georeference",
}


def main() -> None:
    ensure_dirs()
    config = yaml.safe_load((CONFIGS / "project.yml").read_text(encoding="utf-8"))
    rules = yaml.safe_load((CONFIGS / "rule_catalogue.yml").read_text(encoding="utf-8"))["rules"]

    rows: list[dict[str, Any]] = []
    for path in discover_ifc_files(config):
        try:
            model = ifcopenshell.open(str(path))
        except Exception:
            continue
        inv = inventory_row(path, model)
        label = inv["model"]
        for rule in rules:
            check = rule["check"]
            for obj in applicable_objects(model, rule["target_classes"]):
                feature = feature_from_object(label, obj)
                ok, _ = evaluate_feature(feature, rule)
                if ok:
                    mutated = make_feature_mutation(feature, rule, should_pass=False)
                    mutated_ok, _ = evaluate_feature(mutated, rule)
                    rows.append(
                        {
                            "model": label,
                            "source_repository": inv["source_repository"],
                            "schema": inv["schema"],
                            "completeness_tier": inv["completeness_tier"],
                            "rule_id": rule["rule_id"],
                            "operator": NEGATIVE_OPERATOR[check],
                            "original_state": "pass",
                            "expected_mutated_state": "fail",
                            "mutation_success": not mutated_ok,
                        }
                    )
                else:
                    mutated = make_feature_mutation(feature, rule, should_pass=True)
                    mutated_ok, _ = evaluate_feature(mutated, rule)
                    rows.append(
                        {
                            "model": label,
                            "source_repository": inv["source_repository"],
                            "schema": inv["schema"],
                            "completeness_tier": inv["completeness_tier"],
                            "rule_id": rule["rule_id"],
                            "operator": POSITIVE_OPERATOR[check],
                            "original_state": "fail",
                            "expected_mutated_state": "pass",
                            "mutation_success": mutated_ok,
                        }
                    )

    detail = pd.DataFrame(rows)
    detail.to_csv(DATA_PROCESSED / "mutation_repair_simulation_detail.csv", index=False)
    summary = (
        detail.groupby(["rule_id", "operator", "original_state", "expected_mutated_state"], as_index=False)
        .agg(test_count=("mutation_success", "size"), success_count=("mutation_success", "sum"))
        .sort_values(["rule_id", "original_state", "operator"])
    )
    summary["success_rate"] = summary["success_count"] / summary["test_count"].where(summary["test_count"] != 0)
    summary.to_csv(DATA_PROCESSED / "mutation_repair_operator_summary.csv", index=False)
    summary.to_csv(TABLES / "table11_mutation_repair_operator_summary.csv", index=False)

    by_tier = (
        detail.groupby(["completeness_tier", "rule_id", "original_state"], as_index=False)
        .agg(test_count=("mutation_success", "size"), success_count=("mutation_success", "sum"))
        .sort_values(["completeness_tier", "rule_id", "original_state"])
    )
    by_tier["success_rate"] = by_tier["success_count"] / by_tier["test_count"].where(by_tier["test_count"] != 0)
    by_tier.to_csv(DATA_PROCESSED / "mutation_repair_by_tier.csv", index=False)
    by_tier.to_csv(TABLES / "table_s3_mutation_repair_by_tier.csv", index=False)


if __name__ == "__main__":
    main()
