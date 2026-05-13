from __future__ import annotations

from typing import Any

import ifcopenshell
import pandas as pd
import yaml

from aic_openbim_acc.corpus import discover_ifc_files, inventory_row
from aic_openbim_acc.ifc_rules import applicable_objects, evaluate_feature, feature_from_object, normalize_length
from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, TABLES, ensure_dirs


ACTION_MAP = {
    "R01_GLOBAL_ID": ("information_continuity", "model_author", "ensure stable object identifiers before exchange"),
    "R02_OBJECT_NAME": ("information_continuity", "model_author", "supply object names for review traceability"),
    "R03_TYPE_OR_OBJECTTYPE": ("semantic_definition", "model_manager", "define object type, predefined type or type relation"),
    "R04_SPATIAL_CONTAINMENT": ("spatial_project_context", "bim_coordinator", "validate spatial containment and decomposition"),
    "R05_MATERIAL_AVAILABLE": ("material_product_evidence", "designer_or_product_data_owner", "attach material assignment"),
    "R06_DOOR_CLEAR_WIDTH": ("regulatory_attributes", "architect_or_bim_coordinator", "supply width evidence or geometry route"),
    "R07_WINDOW_DIMENSIONS": ("regulatory_attributes", "facade_or_bim_author", "supply window width and height evidence"),
    "R08_SPACE_AREA": ("regulatory_attributes", "architect_or_space_planner", "supply positive space area quantity/property"),
    "R09_FIRE_RATING": ("regulatory_attributes", "fire_designer_or_product_data_owner", "supply fire-rating property/classification"),
    "R10_SITE_GEOREFERENCE": ("spatial_project_context", "survey_or_bim_manager", "define site georeferencing evidence"),
}


def route_for(feature: Any, rule: dict[str, Any], ok: bool, reason: str) -> tuple[str, str, str]:
    rid = rule["rule_id"]
    if rid in {"R01_GLOBAL_ID", "R02_OBJECT_NAME", "R07_WINDOW_DIMENSIONS", "R10_SITE_GEOREFERENCE"}:
        return ("E2" if ok else "E0", "direct_attribute" if ok else "missing_direct_attribute", reason)
    if rid == "R03_TYPE_OR_OBJECTTYPE":
        if feature.object_type:
            return ("E2", "direct_object_type", reason)
        if feature.predefined_type and str(feature.predefined_type).upper() != "NOTDEFINED":
            return ("E2", "predefined_type", reason)
        if feature.has_type:
            return ("E3", "type_relationship", reason)
        return ("E0", "missing_type_route", reason)
    if rid == "R04_SPATIAL_CONTAINMENT":
        return ("E4" if ok else "E0", "spatial_relationship" if ok else "missing_spatial_relationship", reason)
    if rid == "R05_MATERIAL_AVAILABLE":
        return ("E4" if ok else "E0", "material_relationship" if ok else "missing_material_relationship", reason)
    if rid == "R06_DOOR_CLEAR_WIDTH":
        value = normalize_length(feature.attributes.get("OverallWidth"))
        if ok:
            return ("E2", "direct_numeric_attribute_threshold", reason)
        if value is not None:
            return ("E1", "raw_width_present_below_threshold", reason)
        return ("E0", "missing_width_attribute", reason)
    if rid == "R08_SPACE_AREA":
        if ok:
            return ("E4", "quantity_or_property_route", reason)
        return ("E0", "missing_area_quantity_or_property", reason)
    if rid == "R09_FIRE_RATING":
        if ok and "property" in reason.lower():
            return ("E3", "fire_rating_property", reason)
        if ok and "token" in reason.lower():
            return ("E1", "name_or_type_token", reason)
        return ("E0", "missing_fire_rating_route", reason)
    return ("E0", "unsupported", reason)


def triage_state(route_tier: str, passed: bool) -> str:
    if passed:
        return "ready"
    if route_tier == "E1":
        return "evidence_present_but_insufficient"
    return "missing_evidence"


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
            family, actor, action = ACTION_MAP[rule["rule_id"]]
            for obj in applicable_objects(model, rule["target_classes"]):
                feature = feature_from_object(label, obj)
                ok, reason = evaluate_feature(feature, rule)
                tier, route_type, locator = route_for(feature, rule, ok, reason)
                rows.append(
                    {
                        "model": label,
                        "schema": inv["schema"],
                        "source_repository": inv["source_repository"],
                        "model_type": inv["model_type"],
                        "completeness_tier": inv["completeness_tier"],
                        "rule_id": rule["rule_id"],
                        "evidence_family": family,
                        "ifc_class": feature.ifc_class,
                        "global_id": feature.global_id,
                        "passed": ok,
                        "route_tier": tier,
                        "route_type": route_type,
                        "evidence_locator": locator,
                        "triage_state": triage_state(tier, ok),
                        "responsible_actor": actor,
                        "suggested_action": action,
                    }
                )

    routes = pd.DataFrame(rows)
    routes.to_csv(DATA_PROCESSED / "evidence_route_element_level.csv", index=False)
    summary = (
        routes.groupby(["rule_id", "evidence_family", "route_tier", "route_type", "triage_state"], as_index=False)
        .size()
        .rename(columns={"size": "object_count"})
        .sort_values(["rule_id", "route_tier", "route_type"])
    )
    summary.to_csv(DATA_PROCESSED / "evidence_route_graph_summary.csv", index=False)
    summary.to_csv(TABLES / "table9_evidence_route_graph_summary.csv", index=False)

    state_counts = routes.groupby(["evidence_family", "triage_state"], as_index=False).size().rename(
        columns={"size": "item_count"}
    )
    scenarios = {
        "opaque_checking_low": {"missing_evidence": 5, "evidence_present_but_insufficient": 5, "ready": 0},
        "opaque_checking_base": {"missing_evidence": 15, "evidence_present_but_insufficient": 15, "ready": 0},
        "opaque_checking_high": {"missing_evidence": 30, "evidence_present_but_insufficient": 30, "ready": 0},
        "rulebridge_triage_low": {"missing_evidence": 1, "evidence_present_but_insufficient": 3, "ready": 0},
        "rulebridge_triage_base": {"missing_evidence": 5, "evidence_present_but_insufficient": 10, "ready": 0},
        "rulebridge_triage_high": {"missing_evidence": 10, "evidence_present_but_insufficient": 20, "ready": 0},
    }
    sim_rows = []
    for scenario, minutes in scenarios.items():
        for _, row in state_counts.iterrows():
            state = row["triage_state"]
            sim_rows.append(
                {
                    "scenario": scenario,
                    "evidence_family": row["evidence_family"],
                    "triage_state": state,
                    "item_count": int(row["item_count"]),
                    "minutes_per_item": minutes[state],
                    "workload_minutes": int(row["item_count"]) * minutes[state],
                }
            )
    sim = pd.DataFrame(sim_rows)
    sim.to_csv(DATA_PROCESSED / "project_delivery_triage_simulation.csv", index=False)
    sim.to_csv(TABLES / "table10_project_delivery_triage_simulation.csv", index=False)

    model_class = (
        routes.groupby(["model", "source_repository", "schema", "model_type", "completeness_tier"], as_index=False)
        .agg(total_items=("rule_id", "size"), ready_items=("passed", "sum"))
    )
    model_class["ready_share"] = model_class["ready_items"] / model_class["total_items"].where(
        model_class["total_items"] != 0
    )
    model_class["submission_readiness_class"] = pd.cut(
        model_class["ready_share"],
        bins=[-0.01, 0.5, 0.8, 1.0],
        labels=["high-risk", "partially-ready", "mostly-ready"],
    )
    model_class.to_csv(DATA_PROCESSED / "model_submission_readiness_class.csv", index=False)


if __name__ == "__main__":
    main()
