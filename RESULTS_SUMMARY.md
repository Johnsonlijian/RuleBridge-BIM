# Pilot Results Summary

Run date: 2026-04-29

## Corpora

The pilot processed:

- **4,329** annotated CODE-ACCORD relation pairs.
- **315** direct numeric relations: greater-equal, greater, less-equal, less and equal.
- **3,002** semantic precondition relations: necessity, selection and part-of.
- **12** public IDS example files.
- **38** IDS specifications and **226** IDS facets.
- **24** public IFC models across IFC2X3, IFC4 and IFC4X3.
- **2,937** applicable IfcElement targets for identifier/type checks.

## Rule-Level Results

| Rule | Interpretation | Pass rate |
|---|---|---:|
| R01_GLOBAL_ID | Stable identifiers | 100.0% |
| R02_OBJECT_NAME | Object naming | 99.97% |
| R03_TYPE_OR_OBJECTTYPE | Semantic typing | 99.28% |
| R04_SPATIAL_CONTAINMENT | Spatial assignment | 84.81% |
| R05_MATERIAL_AVAILABLE | Material information | 97.21% |
| R06_DOOR_CLEAR_WIDTH | Door width availability/minimum | 69.84% |
| R07_WINDOW_DIMENSIONS | Window width/height | 100.0% |
| R08_SPACE_AREA | Space area availability | 83.33% |
| R09_FIRE_RATING | Fire-rating evidence | 46.40% |
| R10_SITE_GEOREFERENCE | Site georeferencing | 2.00% |

## Main Findings

1. Public IFC models usually carry identifiers and object names, so traceability is not the main bottleneck in this pilot.
2. Automated checking readiness drops for information that bridges design intent and regulatory judgement: georeferencing, fire ratings, clear-width evidence, space areas and spatial containment.
3. The CODE-ACCORD relation distribution supports a two-stage strategy: direct numeric relations can become executable comparisons, while semantic relations become IDS-style information preconditions.
4. Counterfactual checks detected injected violations and accepted synthetic repairs for supported rules, giving a basic implementation sanity check.

## Manuscript Claim Boundaries

These are not claims about the compliance of real buildings. They are claims about **OpenBIM information readiness for automated compliance checking**. The current IFC corpus contains public samples, not a representative regulatory-submission dataset.

