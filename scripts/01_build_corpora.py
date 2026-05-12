from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd
import yaml

from aic_openbim_acc.paths import CONFIGS, DATA_PROCESSED, DATA_RAW, ensure_dirs


COMPARATIVE_RELATIONS = {"greater-equal", "greater", "less-equal", "less", "equal"}


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def extract_pair(tagged: str) -> tuple[str | None, str | None]:
    e1 = re.search(r"<e1>(.*?)</e1>", tagged)
    e2 = re.search(r"<e2>(.*?)</e2>", tagged)
    return (e1.group(1) if e1 else None, e2.group(1) if e2 else None)


def code_accord_stats(code_root: Path) -> None:
    entity_path = code_root / "annotated_data" / "entities" / "all.csv"
    relation_path = code_root / "annotated_data" / "relations" / "all.csv"
    entities = pd.read_csv(entity_path)
    relations = pd.read_csv(relation_path)

    relation_stats = (
        relations["relation_type"]
        .value_counts()
        .rename_axis("relation_type")
        .reset_index(name="n_relations")
    )
    relation_stats["machine_checkable_tier"] = relation_stats["relation_type"].map(
        lambda x: "direct_numeric" if x in COMPARATIVE_RELATIONS else ("semantic_precondition" if x in {"necessity", "selection", "part-of"} else "not_direct")
    )
    relation_stats.to_csv(DATA_PROCESSED / "code_accord_relation_stats.csv", index=False)

    candidates = relations[relations["relation_type"].isin(COMPARATIVE_RELATIONS | {"necessity"})].copy()
    pairs = candidates["tagged_sentence"].map(extract_pair)
    candidates["entity_1"] = [p[0] for p in pairs]
    candidates["entity_2"] = [p[1] for p in pairs]
    candidates = candidates[
        ["example_id", "metadata", "relation_type", "entity_1", "entity_2", "content", "tagged_sentence"]
    ]
    candidates.to_csv(DATA_PROCESSED / "code_accord_rule_candidates.csv", index=False)

    label_counter: Counter[str] = Counter()
    for labels in entities["label"].astype(str):
        for item in labels.split():
            if item != "O":
                label_counter[item.replace("B-", "").replace("I-", "")] += 1
    pd.DataFrame(
        [{"entity_label": key, "n_tokens": value} for key, value in sorted(label_counter.items())]
    ).to_csv(DATA_PROCESSED / "code_accord_entity_label_stats.csv", index=False)

    summary = pd.DataFrame(
        [
            {"corpus": "CODE-ACCORD entities", "records": len(entities), "files": 1},
            {"corpus": "CODE-ACCORD relations", "records": len(relations), "files": 1},
            {"corpus": "CODE-ACCORD candidate rules", "records": len(candidates), "files": 1},
        ]
    )
    summary.to_csv(DATA_PROCESSED / "code_accord_summary.csv", index=False)


def ids_stats(ids_root: Path) -> None:
    example_dir = ids_root / "Documentation" / "Examples"
    rows = []
    facet_rows = []
    for path in sorted(example_dir.glob("*.ids")):
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        root = tree.getroot()
        specs = [el for el in root.iter() if local_name(el.tag) == "specification"]
        facet_counts: Counter[str] = Counter()
        for spec in specs:
            for el in spec.iter():
                name = local_name(el.tag)
                if name in {"entity", "attribute", "property", "classification", "material", "partOf"}:
                    facet_counts[name] += 1
        rows.append(
            {
                "ids_file": path.name,
                "n_specifications": len(specs),
                "n_facets": sum(facet_counts.values()),
                **{f"facet_{key}": facet_counts.get(key, 0) for key in ["entity", "attribute", "property", "classification", "material", "partOf"]},
            }
        )
        for key, value in facet_counts.items():
            facet_rows.append({"ids_file": path.name, "facet": key, "n": value})
    pd.DataFrame(rows).to_csv(DATA_PROCESSED / "ids_example_stats.csv", index=False)
    pd.DataFrame(facet_rows).to_csv(DATA_PROCESSED / "ids_facet_long.csv", index=False)


def main() -> None:
    ensure_dirs()
    config = yaml.safe_load((CONFIGS / "project.yml").read_text(encoding="utf-8"))
    code_accord_stats(DATA_RAW / Path(config["paths"]["code_accord"]).name)
    ids_stats(DATA_RAW / Path(config["paths"]["ids_repo"]).name)

    summaries = []
    for path in [
        DATA_PROCESSED / "code_accord_summary.csv",
        DATA_PROCESSED / "ids_example_stats.csv",
    ]:
        df = pd.read_csv(path)
        summaries.append({"artifact": path.name, "rows": len(df), "columns": len(df.columns)})
    pd.DataFrame(summaries).to_csv(DATA_PROCESSED / "corpus_artifact_manifest.csv", index=False)


if __name__ == "__main__":
    main()

