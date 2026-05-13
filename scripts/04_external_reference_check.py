from __future__ import annotations

from typing import Any

import ifcopenshell
import ifcopenshell.util.element as ifc_element
import pandas as pd
import yaml

from aic_openbim_acc.corpus import discover_ifc_files, inventory_row
from aic_openbim_acc.ifc_rules import applicable_objects, feature_from_object, normalize_length
from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, ensure_dirs


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip() not in {"<None>", "None", "NULL"}
    return True


def _direct_containment(obj: Any) -> bool:
    try:
        return bool(getattr(obj, "ContainedInStructure"))
    except Exception:
        return False


def _direct_material(obj: Any) -> bool:
    try:
        return ifc_element.get_material(obj) is not None
    except Exception:
        return False


def direct_reference_pass(obj: Any, feature: Any, rule: dict[str, Any]) -> bool:
    """A deliberately simple IfcOpenShell direct-field reference.

    This is not a competing ACC/IDS system. It is a separate direct extraction
    reference used to check whether RuleBridge-BIM adds evidence-routing logic
    beyond raw field presence or applies stricter task-specific criteria.
    """

    rid = rule["rule_id"]
    if rid == "R01_GLOBAL_ID":
        return _non_empty(getattr(obj, "GlobalId", None))
    if rid == "R02_OBJECT_NAME":
        return _non_empty(getattr(obj, "Name", None))
    if rid == "R03_TYPE_OR_OBJECTTYPE":
        return _non_empty(getattr(obj, "ObjectType", None))
    if rid == "R04_SPATIAL_CONTAINMENT":
        return _direct_containment(obj)
    if rid == "R05_MATERIAL_AVAILABLE":
        return _direct_material(obj)
    if rid == "R06_DOOR_CLEAR_WIDTH":
        return normalize_length(getattr(obj, "OverallWidth", None)) is not None
    if rid == "R07_WINDOW_DIMENSIONS":
        return (
            normalize_length(getattr(obj, "OverallWidth", None)) is not None
            and normalize_length(getattr(obj, "OverallHeight", None)) is not None
        )
    if rid == "R08_SPACE_AREA":
        for name in rule.get("property_names", []):
            if str(name).lower() in feature.property_names:
                return True
        return False
    if rid == "R09_FIRE_RATING":
        for name in rule.get("property_names", []):
            if str(name).lower() in feature.property_names:
                return True
        text = " ".join(str(x or "") for x in [feature.name, feature.object_type, feature.predefined_type])
        return "EI" in text.upper() or "FIRE" in text.upper()
    if rid == "R10_SITE_GEOREFERENCE":
        return bool(getattr(obj, "RefLatitude", None) and getattr(obj, "RefLongitude", None))
    raise ValueError(f"Unsupported direct reference rule: {rid}")


def main() -> None:
    ensure_dirs()
    config = yaml.safe_load((CONFIGS / "project.yml").read_text(encoding="utf-8"))
    rules = yaml.safe_load((CONFIGS / "rule_catalogue.yml").read_text(encoding="utf-8"))["rules"]
    rb = pd.read_csv(DATA_PROCESSED / "rule_results_model_level.csv")
    rb_summary = (
        rb.groupby("rule_id", as_index=False)
        .agg(rulebridge_target_count=("target_count", "sum"), rulebridge_pass_count=("pass_count", "sum"))
    )

    rows: list[dict[str, Any]] = []
    for path in discover_ifc_files(config):
        try:
            model = ifcopenshell.open(str(path))
        except Exception:
            continue
        inv = inventory_row(path, model)
        label = inv["model"]
        for rule in rules:
            direct_pass_count = 0
            target_count = 0
            for obj in applicable_objects(model, rule["target_classes"]):
                target_count += 1
                feature = feature_from_object(label, obj)
                direct_pass_count += int(direct_reference_pass(obj, feature, rule))
            rows.append(
                {
                    "model": label,
                    "source_repository": inv["source_repository"],
                    "model_type": inv["model_type"],
                    "completeness_tier": inv["completeness_tier"],
                    "schema": model.schema,
                    "rule_id": rule["rule_id"],
                    "target_count": target_count,
                    "direct_reference_pass_count": direct_pass_count,
                    "direct_reference_pass_rate": direct_pass_count / target_count if target_count else None,
                }
            )

    direct = pd.DataFrame(rows)
    direct_summary = (
        direct.groupby("rule_id", as_index=False)
        .agg(
            direct_target_count=("target_count", "sum"),
            direct_reference_pass_count=("direct_reference_pass_count", "sum"),
        )
    )
    out = rb_summary.merge(direct_summary, on="rule_id", how="outer")
    out["target_count_match"] = out["rulebridge_target_count"] == out["direct_target_count"]
    out["rulebridge_pass_rate"] = out["rulebridge_pass_count"] / out["rulebridge_target_count"]
    out["direct_reference_pass_rate"] = out["direct_reference_pass_count"] / out["direct_target_count"]
    out["difference_rulebridge_minus_direct"] = out["rulebridge_pass_rate"] - out["direct_reference_pass_rate"]
    out.to_csv(DATA_PROCESSED / "external_ifcopenshell_direct_reference.csv", index=False)
    direct.to_csv(DATA_PROCESSED / "external_ifcopenshell_direct_reference_by_model.csv", index=False)


if __name__ == "__main__":
    main()
