# Results Summary

Run date: 2026-05-13

## Corpora

The ITcon R19 diagnostic package processed:

- **4,329** annotated CODE-ACCORD relation pairs.
- **315** direct numeric candidate relations: greater-equal, greater, less-equal, less and equal.
- **3,002** semantic information-precondition relations: necessity, selection and part-of.
- **12** public IDS example files.
- **344** discovered public IFC files.
- **341** successfully parsed IFC files across IFC2X3, IFC4 and IFC4X3.
- **34,554** object-rule evaluations across parsed target-bearing models.

The public IFC corpus is stratified as complete-ish models, sample fragments and IDS-oriented test fragments. It is reproducible and useful for benchmark stress-testing, but it is not treated as representative of permit submissions.

## Expanded Evidence-Readiness Results

| Completeness stratum | Information continuity | Semantic definition | Spatial/project context | Material/product evidence | Regulatory attributes |
|---|---:|---:|---:|---:|---:|
| Complete-ish | 97.56% | 46.82% | 91.09% | 85.94% | 34.33% |
| Sample-fragment | 100.00% | 97.57% | 87.88% | 100.00% | 7.14% |
| Test-fragment | 58.10% | 12.23% | 12.53% | 10.06% | 3.49% |

## IDS/IfcTester Reference Comparison

RuleBridge-BIM was compared with an IDS/IfcTester reference for the IDS-expressible subset of checks:

- Exact agreement for GlobalId, object name, material and window dimension checks.
- **421** RuleBridge-only passes for type evidence because RuleBridge accepts predefined type and type-relationship routes beyond direct object type.
- **50** IfcTester-only passes for door width because the IDS reference checks width presence, while RuleBridge-BIM applies the illustrative threshold.
- R04 spatial containment and R10 site georeferencing are reported as not represented by the pilot IDS mapping.

## Evidence Route Graph And Triage

The Evidence Route Graph distinguishes direct attributes, predefined/type routes, relationship routes, quantity/property routes, missing evidence and evidence-present-but-insufficient cases. Key diagnostic gaps include:

- **873** missing spatial relationship cases.
- **1,635** missing fire-rating route cases.
- **103** missing door-width cases and **50** width-present-but-insufficient cases.
- **99** missing site georeference cases.

The mutation/repair simulation generated **34,554** synthetic test rows. Implemented operators followed the expected deterministic state transitions, supporting implementation maintainability but not legal correctness.

## Claim Boundaries

These are not claims about the compliance of real buildings. They are claims about **OpenBIM evidence readiness and pre-compliance information governance before automated compliance checking**. The current IFC corpus contains public samples and test fragments, not a representative regulatory-submission dataset.
