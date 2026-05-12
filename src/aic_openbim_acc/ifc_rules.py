from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import ifcopenshell
import ifcopenshell.util.element as ifc_element


FIRE_TOKEN = re.compile(r"\b(EI|REI|R|E)\s*[-]?\s*\d{2,3}\b", re.IGNORECASE)


@dataclass
class ElementFeature:
    model_name: str
    ifc_class: str
    global_id: str | None
    name: str | None
    object_type: str | None
    predefined_type: str | None
    attributes: dict[str, Any]
    properties: dict[str, Any]
    property_names: set[str]
    has_material: bool
    has_containment: bool
    has_type: bool


def _safe_attr(obj: Any, name: str) -> Any:
    try:
        return getattr(obj, name)
    except Exception:
        return None


def _flatten_psets(obj: Any) -> dict[str, Any]:
    values: dict[str, Any] = {}
    try:
        psets = ifc_element.get_psets(obj)
    except Exception:
        return values
    for pset_name, props in psets.items():
        if not isinstance(props, dict):
            continue
        for prop_name, prop_value in props.items():
            if prop_name == "id":
                continue
            values[prop_name] = prop_value
            values[f"{pset_name}.{prop_name}"] = prop_value
    return values


def _has_containment(obj: Any) -> bool:
    for attr in ["ContainedInStructure", "Decomposes"]:
        value = _safe_attr(obj, attr)
        if value:
            return True
    return False


def _has_type(obj: Any) -> bool:
    if _safe_attr(obj, "IsTypedBy"):
        return True
    if _safe_attr(obj, "ObjectType"):
        return True
    predefined = _safe_attr(obj, "PredefinedType")
    return bool(predefined and str(predefined).upper() != "NOTDEFINED")


def feature_from_object(model_name: str, obj: Any) -> ElementFeature:
    props = _flatten_psets(obj)
    try:
        material = ifc_element.get_material(obj)
    except Exception:
        material = None
    attrs = {}
    for attr in [
        "GlobalId",
        "Name",
        "Description",
        "ObjectType",
        "PredefinedType",
        "Tag",
        "OverallWidth",
        "OverallHeight",
        "RefLatitude",
        "RefLongitude",
    ]:
        value = _safe_attr(obj, attr)
        if value is not None:
            attrs[attr] = value
    return ElementFeature(
        model_name=model_name,
        ifc_class=obj.is_a(),
        global_id=_safe_attr(obj, "GlobalId"),
        name=_safe_attr(obj, "Name"),
        object_type=_safe_attr(obj, "ObjectType"),
        predefined_type=_safe_attr(obj, "PredefinedType"),
        attributes=attrs,
        properties=props,
        property_names={str(k).lower() for k in props.keys()},
        has_material=material is not None,
        has_containment=_has_containment(obj),
        has_type=_has_type(obj),
    )


def normalize_length(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return number
    return number / 1000.0 if number > 10 else number


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip() not in {"<None>", "None", "NULL"}
    return True


def evaluate_feature(feature: ElementFeature, rule: dict[str, Any]) -> tuple[bool, str]:
    check = rule["check"]

    if check == "required_attribute":
        attr = rule["attribute"]
        ok = _non_empty(feature.attributes.get(attr))
        return ok, f"{attr} is present" if ok else f"{attr} is missing"

    if check == "type_or_object_type":
        ok = feature.has_type
        return ok, "type/object type is present" if ok else "type/object type is missing"

    if check == "containment_required":
        ok = feature.has_containment
        return ok, "spatial containment is present" if ok else "spatial containment is missing"

    if check == "material_assigned":
        ok = feature.has_material
        return ok, "material assignment is present" if ok else "material assignment is missing"

    if check == "numeric_attribute_min":
        attr = rule["attribute"]
        value = normalize_length(feature.attributes.get(attr))
        min_value = float(rule["min_value"])
        ok = value is not None and value >= min_value
        return ok, f"{attr}={value}" if ok else f"{attr} is missing or below {min_value} m"

    if check == "numeric_attributes_positive":
        missing = []
        for attr in rule["attributes"]:
            value = normalize_length(feature.attributes.get(attr))
            if value is None or value <= 0:
                missing.append(attr)
        ok = not missing
        return ok, "all dimensions are positive" if ok else f"missing/non-positive dimensions: {', '.join(missing)}"

    if check == "property_any_positive":
        for name in rule["property_names"]:
            for key, value in feature.properties.items():
                if key.lower().endswith(str(name).lower()):
                    try:
                        number = float(value)
                    except (TypeError, ValueError):
                        if _non_empty(value):
                            return True, f"{key} is present"
                    else:
                        if number > 0:
                            return True, f"{key}={number}"
        return False, "no positive area property found"

    if check == "fire_rating_available":
        lower_names = feature.property_names
        for name in rule.get("property_names", []):
            if str(name).lower() in lower_names:
                return True, f"{name} property is present"
        text = " ".join(str(x or "") for x in [feature.name, feature.object_type, feature.predefined_type])
        if FIRE_TOKEN.search(text):
            return True, "fire rating token found in type/name"
        return False, "fire rating property/token is missing"

    if check == "site_georeferenced":
        lat = feature.attributes.get("RefLatitude")
        lon = feature.attributes.get("RefLongitude")
        ok = bool(lat and lon)
        return ok, "site latitude/longitude are present" if ok else "site latitude/longitude are missing"

    raise ValueError(f"Unsupported check: {check}")


def make_feature_mutation(feature: ElementFeature, rule: dict[str, Any], should_pass: bool) -> ElementFeature:
    mutated = ElementFeature(
        model_name=feature.model_name,
        ifc_class=feature.ifc_class,
        global_id=feature.global_id,
        name=feature.name,
        object_type=feature.object_type,
        predefined_type=feature.predefined_type,
        attributes=dict(feature.attributes),
        properties=dict(feature.properties),
        property_names=set(feature.property_names),
        has_material=feature.has_material,
        has_containment=feature.has_containment,
        has_type=feature.has_type,
    )
    check = rule["check"]
    if should_pass:
        if check == "required_attribute":
            mutated.attributes[rule["attribute"]] = "SYNTHETIC_VALUE"
        elif check == "type_or_object_type":
            mutated.has_type = True
        elif check == "containment_required":
            mutated.has_containment = True
        elif check == "material_assigned":
            mutated.has_material = True
        elif check == "numeric_attribute_min":
            mutated.attributes[rule["attribute"]] = float(rule["min_value"])
        elif check == "numeric_attributes_positive":
            for attr in rule["attributes"]:
                mutated.attributes[attr] = 1.0
        elif check == "property_any_positive":
            mutated.properties[rule["property_names"][0]] = 1.0
            mutated.property_names.add(str(rule["property_names"][0]).lower())
        elif check == "fire_rating_available":
            mutated.properties[rule["property_names"][0]] = "EI60"
            mutated.property_names.add(str(rule["property_names"][0]).lower())
        elif check == "site_georeferenced":
            mutated.attributes["RefLatitude"] = (51, 30, 0, 0)
            mutated.attributes["RefLongitude"] = (0, 7, 0, 0)
    else:
        if check == "required_attribute":
            mutated.attributes[rule["attribute"]] = None
        elif check == "type_or_object_type":
            mutated.has_type = False
            mutated.attributes["ObjectType"] = None
            mutated.attributes["PredefinedType"] = None
            mutated.object_type = None
            mutated.predefined_type = None
        elif check == "containment_required":
            mutated.has_containment = False
        elif check == "material_assigned":
            mutated.has_material = False
        elif check == "numeric_attribute_min":
            mutated.attributes[rule["attribute"]] = 0.1
        elif check == "numeric_attributes_positive":
            for attr in rule["attributes"]:
                mutated.attributes[attr] = None
        elif check == "property_any_positive":
            mutated.properties.clear()
            mutated.property_names.clear()
        elif check == "fire_rating_available":
            for name in rule.get("property_names", []):
                mutated.properties.pop(name, None)
                mutated.property_names.discard(str(name).lower())
            mutated.name = "SYNTHETIC_OBJECT"
            mutated.object_type = "SYNTHETIC_TYPE"
        elif check == "site_georeferenced":
            mutated.attributes["RefLatitude"] = None
            mutated.attributes["RefLongitude"] = None
    return mutated


def applicable_objects(model: ifcopenshell.file, target_classes: list[str]) -> list[Any]:
    seen: set[int] = set()
    objects: list[Any] = []
    for cls in target_classes:
        try:
            candidates = model.by_type(cls)
        except Exception:
            candidates = []
        for obj in candidates:
            if obj.id() not in seen:
                objects.append(obj)
                seen.add(obj.id())
    return objects

