from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ifcopenshell
import pandas as pd
import yaml
from ifctester.ids import Attribute, Entity, Ids, Material, Property, Specification

from aic_openbim_acc.corpus import discover_ifc_files, inventory_row
from aic_openbim_acc.ifc_rules import applicable_objects, feature_from_object
from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, TABLES, ensure_dirs


IDS_DIR = CONFIGS / "ids_reference"
IDS_FILE = IDS_DIR / "rulebridge_ifctester_reference.ids"

IDS_ELEMENT_CLASSES = [
    "IfcAirTerminal",
    "IfcBeam",
    "IfcBuildingElementPart",
    "IfcBuildingElementProxy",
    "IfcChimney",
    "IfcColumn",
    "IfcCourse",
    "IfcCovering",
    "IfcDiscreteAccessory",
    "IfcDistributionElement",
    "IfcDoor",
    "IfcDuctSegment",
    "IfcEarthworksFill",
    "IfcElementAssembly",
    "IfcFlowSegment",
    "IfcFlowTerminal",
    "IfcFooting",
    "IfcFurnishingElement",
    "IfcFurniture",
    "IfcGeographicElement",
    "IfcMechanicalFastener",
    "IfcMember",
    "IfcOpeningElement",
    "IfcPipeSegment",
    "IfcPlate",
    "IfcRail",
    "IfcRailing",
    "IfcRamp",
    "IfcRampFlight",
    "IfcRoof",
    "IfcSanitaryTerminal",
    "IfcSign",
    "IfcSlab",
    "IfcStair",
    "IfcStairFlight",
    "IfcSurfaceFeature",
    "IfcTrackElement",
    "IfcVirtualElement",
    "IfcWall",
    "IfcWallStandardCase",
    "IfcWindow",
]

IDS_TARGET_EXPANSION = {
    "IfcElement": IDS_ELEMENT_CLASSES,
    "IfcWall": ["IfcWall", "IfcWallStandardCase"],
}


@dataclass(frozen=True)
class IdsRoute:
    rule_id: str
    route_id: str
    target_class: str
    requirements: tuple[Any, ...]


def rule_routes(rule: dict[str, Any]) -> list[IdsRoute]:
    rid = rule["rule_id"]
    expanded_targets: list[str] = []
    for target in rule["target_classes"]:
        expanded_targets.extend(IDS_TARGET_EXPANSION.get(str(target), [str(target)]))
    targets = sorted({c.upper() for c in expanded_targets})
    routes: list[IdsRoute] = []
    for cls in targets:
        if rid == "R01_GLOBAL_ID":
            routes.append(IdsRoute(rid, "attribute_GlobalId", cls, (Attribute("GlobalId"),)))
        elif rid == "R02_OBJECT_NAME":
            routes.append(IdsRoute(rid, "attribute_Name", cls, (Attribute("Name"),)))
        elif rid == "R03_TYPE_OR_OBJECTTYPE":
            routes.append(IdsRoute(rid, "attribute_ObjectType", cls, (Attribute("ObjectType"),)))
        elif rid == "R05_MATERIAL_AVAILABLE":
            routes.append(IdsRoute(rid, "material_required", cls, (Material(),)))
        elif rid == "R06_DOOR_CLEAR_WIDTH":
            routes.append(IdsRoute(rid, "attribute_OverallWidth", cls, (Attribute("OverallWidth"),)))
        elif rid == "R07_WINDOW_DIMENSIONS":
            routes.append(
                IdsRoute(
                    rid,
                    "attribute_OverallWidth_OverallHeight",
                    cls,
                    (Attribute("OverallWidth"), Attribute("OverallHeight")),
                )
            )
        elif rid == "R08_SPACE_AREA":
            for pset, prop in [
                ("Qto_SpaceBaseQuantities", "NetFloorArea"),
                ("Qto_SpaceBaseQuantities", "GrossFloorArea"),
                ("BaseQuantities", "NetFloorArea"),
                ("BaseQuantities", "GrossFloorArea"),
            ]:
                routes.append(IdsRoute(rid, f"property_{pset}_{prop}", cls, (Property(pset, prop),)))
        elif rid == "R09_FIRE_RATING":
            psets = ["Pset_DoorCommon"] if cls == "IFCDOOR" else ["Pset_WallCommon"]
            for pset in psets:
                for prop in ["FireRating", "FireResistanceRating"]:
                    routes.append(IdsRoute(rid, f"property_{pset}_{prop}", cls, (Property(pset, prop),)))
    return routes


def make_ids(routes: list[IdsRoute]) -> Ids:
    ids = Ids(
        title="RuleBridge-BIM IDS-style reference",
        description=(
            "IDS-style reference specifications for the subset of RuleBridge-BIM readiness checks "
            "that can be expressed as direct IDS entity, attribute, property or material requirements."
        ),
    )
    for route in routes:
        spec = Specification(name=f"{route.rule_id}:{route.route_id}:{route.target_class}", minOccurs=0)
        spec.identifier = f"{route.rule_id}|{route.route_id}|{route.target_class}"
        spec.applicability.append(Entity(route.target_class))
        spec.requirements.extend(route.requirements)
        ids.specifications.append(spec)
    return ids


def entity_key(obj: Any) -> tuple[str, str]:
    feature = feature_from_object("", obj)
    return (feature.ifc_class, feature.global_id or f"ifc_id:{obj.id()}")


def main() -> None:
    ensure_dirs()
    IDS_DIR.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load((CONFIGS / "project.yml").read_text(encoding="utf-8"))
    rules = yaml.safe_load((CONFIGS / "rule_catalogue.yml").read_text(encoding="utf-8"))["rules"]

    routes: list[IdsRoute] = []
    route_rows: list[dict[str, Any]] = []
    for rule in rules:
        rule_specific_routes = rule_routes(rule)
        routes.extend(rule_specific_routes)
        if rule_specific_routes:
            for route in rule_specific_routes:
                route_rows.append(
                    {
                        "rule_id": route.rule_id,
                        "route_id": route.route_id,
                        "target_class": route.target_class,
                        "ids_representable": True,
                    }
                )
        else:
            route_rows.append(
                {
                    "rule_id": rule["rule_id"],
                    "route_id": "",
                    "target_class": ",".join(rule["target_classes"]),
                    "ids_representable": False,
                }
            )

    ids_doc = make_ids(routes)
    ids_doc.to_xml(str(IDS_FILE))
    pd.DataFrame(route_rows).to_csv(DATA_PROCESSED / "ifctester_ids_route_mapping.csv", index=False)

    element_rows: list[dict[str, Any]] = []
    model_rows: list[dict[str, Any]] = []

    for path in discover_ifc_files(config):
        try:
            model = ifcopenshell.open(str(path))
        except Exception:
            continue
        inv = inventory_row(path, model)
        label = inv["model"]
        ids_doc.validate(model)

        passed_by_rule: dict[str, set[tuple[str, str]]] = {}
        for spec in ids_doc.specifications:
            if not spec.identifier:
                continue
            rule_id = spec.identifier.split("|", 1)[0]
            passed_by_rule.setdefault(rule_id, set())
            for entity in spec.passed_entities:
                passed_by_rule[rule_id].add(entity_key(entity))

        for rule in rules:
            rid = rule["rule_id"]
            representable = bool(rule_routes(rule))
            targets = applicable_objects(model, rule["target_classes"])
            passed_keys = passed_by_rule.get(rid, set())
            pass_count = 0
            for obj in targets:
                feature = feature_from_object(label, obj)
                key = (feature.ifc_class, feature.global_id or f"ifc_id:{obj.id()}")
                ok = representable and key in passed_keys
                pass_count += int(ok)
                element_rows.append(
                    {
                        "model": label,
                        "schema": inv["schema"],
                        "source_repository": inv["source_repository"],
                        "model_type": inv["model_type"],
                        "completeness_tier": inv["completeness_tier"],
                        "rule_id": rid,
                        "ifc_class": feature.ifc_class,
                        "global_id": feature.global_id,
                        "ids_representable": representable,
                        "ifctester_pass": ok,
                    }
                )
            target_count = len(targets)
            model_rows.append(
                {
                    "model": label,
                    "schema": inv["schema"],
                    "source_repository": inv["source_repository"],
                    "model_type": inv["model_type"],
                    "completeness_tier": inv["completeness_tier"],
                    "rule_id": rid,
                    "ids_representable": representable,
                    "target_count": target_count,
                    "ifctester_pass_count": pass_count,
                    "ifctester_pass_rate": pass_count / target_count if target_count and representable else None,
                }
            )

    elem = pd.DataFrame(element_rows)
    by_model = pd.DataFrame(model_rows)
    elem.to_csv(DATA_PROCESSED / "ifctester_reference_element_level.csv", index=False)
    by_model.to_csv(DATA_PROCESSED / "ifctester_reference_by_model.csv", index=False)

    rb = pd.read_csv(DATA_PROCESSED / "rule_results_element_level.csv")
    merged = rb.merge(
        elem,
        on=["model", "rule_id", "ifc_class", "global_id"],
        how="inner",
        suffixes=("_rulebridge", "_ifctester"),
    )
    represented = merged[merged["ids_representable"]].copy()
    represented["rulebridge_pass"] = represented["passed"].astype(bool)
    represented["both_pass"] = represented["rulebridge_pass"] & represented["ifctester_pass"]
    represented["both_fail"] = ~represented["rulebridge_pass"] & ~represented["ifctester_pass"]
    represented["rb_only_pass"] = represented["rulebridge_pass"] & ~represented["ifctester_pass"]
    represented["ids_only_pass"] = ~represented["rulebridge_pass"] & represented["ifctester_pass"]

    agreement = (
        represented.groupby("rule_id", as_index=False)
        .agg(
            compared_objects=("rule_id", "size"),
            both_pass=("both_pass", "sum"),
            both_fail=("both_fail", "sum"),
            rb_only_pass=("rb_only_pass", "sum"),
            ids_only_pass=("ids_only_pass", "sum"),
        )
    )
    agreement["agreement_rate"] = (agreement["both_pass"] + agreement["both_fail"]) / agreement[
        "compared_objects"
    ].where(agreement["compared_objects"] != 0)
    agreement.to_csv(DATA_PROCESSED / "ids_rulebridge_tool_agreement.csv", index=False)
    agreement.to_csv(TABLES / "table7_ids_rulebridge_tool_agreement.csv", index=False)

    summary = (
        by_model.groupby(["rule_id", "ids_representable"], as_index=False)
        .agg(target_count=("target_count", "sum"), ifctester_pass_count=("ifctester_pass_count", "sum"))
    )
    summary["ifctester_pass_rate"] = summary["ifctester_pass_count"] / summary["target_count"].where(
        summary["target_count"] != 0
    )
    summary.to_csv(DATA_PROCESSED / "ifctester_reference_summary.csv", index=False)
    summary.to_csv(TABLES / "table8_ifctester_reference_summary.csv", index=False)


if __name__ == "__main__":
    main()
