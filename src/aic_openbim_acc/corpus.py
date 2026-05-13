from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import ifcopenshell

from aic_openbim_acc.paths import DATA_RAW, ROOT


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


def source_path_label(path: Path) -> str:
    """Record a portable source-relative path instead of a local absolute path."""
    try:
        return str(path.relative_to(DATA_RAW)).replace("\\", "/")
    except ValueError:
        return path.name


def stable_model_id(path: Path) -> str:
    rel = source_path_label(path)
    stem = re.sub(r"[^A-Za-z0-9]+", "-", path.stem).strip("-")[:56] or "ifc-model"
    suffix = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:8]
    return f"{stem}-{suffix}"


def source_repository(path: Path) -> str:
    rel = source_path_label(path)
    if rel == "AdvancedProject.ifc":
        return "BIM Whale IFC samples"
    if rel.startswith("Sample-Test-Files-main/"):
        return "buildingSMART Sample-Test-Files"
    if rel.startswith("IDS-development/"):
        return "buildingSMART IDS repository"
    if rel.startswith("IfcOpenShell-files/"):
        return "IfcOpenShell files"
    if rel.startswith("Community-Sample-Test-Files/"):
        return "buildingSMART community sample files"
    return "local public IFC source"


def model_type_from_path(path: Path) -> str:
    rel = source_path_label(path).lower()
    if "implementersdocumentation/testcases" in rel:
        return "ids-validator-testcase"
    if "documentation/examples" in rel:
        return "ids-example"
    if "architecture" in rel:
        return "architecture"
    if "structural" in rel or "structure" in rel:
        return "structure"
    if "plumbing" in rel or "hvac" in rel or "mep" in rel:
        return "mep"
    if "infra" in rel or "bridge" in rel or "road" in rel or "rail" in rel:
        return "infrastructure"
    if path.name == "AdvancedProject.ifc":
        return "architecture"
    return "test-fragment"


def class_count(model: ifcopenshell.file, ifc_class: str) -> int:
    try:
        return len(model.by_type(ifc_class))
    except Exception:
        return 0


def classify_completeness(row: dict[str, Any]) -> str:
    element_count = int(row.get("IfcElement", 0) or 0)
    building_elements = int(row.get("IfcBuildingElement", 0) or 0)
    has_building = int(row.get("IfcBuilding", 0) or 0) > 0
    has_site = int(row.get("IfcSite", 0) or 0) > 0
    has_discipline = int(row.get("IfcDistributionElement", 0) or 0) > 0
    file_size = float(row.get("file_size_mb", 0.0) or 0.0)

    if has_building and has_site and (element_count >= 100 or building_elements >= 100 or file_size >= 5.0):
        return "complete-ish"
    if has_discipline and element_count >= 20:
        return "discipline-model"
    if element_count <= 5 and file_size < 0.1:
        return "test-fragment"
    if row.get("model_type") in {"ids-validator-testcase", "ids-example"}:
        return "test-fragment"
    return "sample-fragment"


def discover_ifc_files(config: dict[str, Any], expanded: bool = True) -> list[Path]:
    """Discover public IFC inputs.

    The expanded mode scans all local public raw-data folders. Raw files remain
    outside the public repository; only source-relative labels are written to
    derived outputs.
    """
    configured: list[Path] = []
    roots = [DATA_RAW / Path(config["paths"]["building_smart_ifc"]).name]
    for root in roots:
        if root.exists():
            configured.extend(sorted(root.rglob("*.ifc")))
    for item in config["paths"].get("extra_ifc", []):
        path = DATA_RAW / Path(item).name
        if path.exists():
            configured.append(path)

    if not expanded:
        return sorted(dict.fromkeys(configured))

    files = sorted(DATA_RAW.rglob("*.ifc"))
    return sorted(dict.fromkeys(configured + files))


def inventory_row(path: Path, model: ifcopenshell.file | None, parse_error: str = "") -> dict[str, Any]:
    try:
        file_size_mb = round(path.stat().st_size / 1024 / 1024, 3)
    except OSError:
        file_size_mb = None
    safe_parse_error = parse_error
    if safe_parse_error:
        safe_parse_error = safe_parse_error.replace(str(ROOT), "<project>")
        safe_parse_error = safe_parse_error.replace(str(DATA_RAW), "data_raw")
    row: dict[str, Any] = {
        "model": stable_model_id(path),
        "path": source_path_label(path),
        "source_repository": source_repository(path),
        "model_type": model_type_from_path(path),
        "schema": getattr(model, "schema", "") if model is not None else "",
        "file_size_mb": file_size_mb,
        "parse_status": "ok" if model is not None else "failed",
        "parse_error": safe_parse_error,
        "validation_service_status": "not_tested",
        "license_status": "inspect_only_raw_not_redistributed",
    }
    if model is not None:
        for ifc_type in INVENTORY_TYPES:
            row[ifc_type] = class_count(model, ifc_type)
    else:
        for ifc_type in INVENTORY_TYPES:
            row[ifc_type] = 0
    row["has_ifcsite"] = int(row.get("IfcSite", 0) or 0) > 0
    row["has_ifcbuilding"] = int(row.get("IfcBuilding", 0) or 0) > 0
    row["has_ifcspace"] = int(row.get("IfcSpace", 0) or 0) > 0
    row["door_count"] = int(row.get("IfcDoor", 0) or 0)
    row["wall_count"] = int(row.get("IfcWall", 0) or 0)
    row["site_count"] = int(row.get("IfcSite", 0) or 0)
    row["completeness_tier"] = classify_completeness(row) if model is not None else "parse-failed"
    return row
