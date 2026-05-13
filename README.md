# RuleBridge-BIM

RuleBridge-BIM is a reproducible OpenBIM evidence-readiness dataset and diagnostic protocol for automated compliance checking (ACC). The project links regulatory relation labels, IDS-like information requirements, deterministic IFC evidence extraction, object-level readiness traces, field-presence ablation, failure taxonomy and counterfactual rule-sensitivity assessment.

This repository is prepared as the public reproducibility package for the manuscript project. It is not a public dump of the full submission workspace: raw third-party archives, active submission drafts, cover letters, reviewer strategy notes, internal rounds and journal-specific packages are intentionally excluded.

## What the Diagnostic Protocol Does

The pipeline:

1. builds a public artifact registry from CODE-ACCORD, buildingSMART IDS examples and public IFC sample sources;
2. maps regulatory relation labels into bounded machine-checkability tiers;
3. expresses selected information needs as IDS-like evidence requirements;
4. extracts IFC evidence deterministically;
5. reports readiness results for ten evidence-oriented checks;
6. exports object-level readiness verdicts and failure reasons;
7. compares configured checks with a field-presence ablation;
8. runs a lightweight IfcOpenShell direct-field reference check;
9. tests checker sensitivity with counterfactual pass/fail mutations.

The protocol does not claim legal compliance of sampled buildings, does not claim that the IFC samples represent permit submissions, does not claim independently validated clause-level regulatory traceability, and does not claim superiority over existing ACC or IDS tools.

## Current Empirical Scope

- 4,329 annotated CODE-ACCORD relation pairs.
- 315 direct numeric regulatory relation candidates.
- 3,002 semantic precondition relations.
- 12 public IDS example files.
- 38 IDS specifications and 226 IDS facets.
- 24 public IFC models across IFC2X3, IFC4 and IFC4X3.
- 13,782 object-rule readiness evaluations.
- 10 OpenBIM information-readiness checks.
- 141 counterfactual rule-sensitivity assessment rows.

## Repository Layout

```text
configs/                Configuration files used by the diagnostic scripts
data_processed/         Derived tables generated from public inputs
manuscript/figures/     Generated figures for reporting
manuscript/tables/      Generated reporting tables
scripts/                Reproducible pipeline scripts
src/                    Python package code
DATASETS_AND_LINKS.csv  Public source registry
RESULTS_SUMMARY.md      Compact empirical summary
REPRODUCIBLE_RUNBOOK.md Reproduction notes
```

Excluded local folders include `data_raw/`, `data_interim/`, `Submit-AIC-2026/`, `rounds/`, `logs/`, `deliverables/` and active submission manuscripts.

## Reproduce

Create an environment with the dependencies in `pyproject.toml`, then run:

```powershell
$env:PYTHONPATH='src'
python scripts\01_build_corpora.py
python scripts\02_run_openbim_checks.py
python scripts\03_make_figures.py
python scripts\04_external_reference_check.py
```

Raw public data should be obtained from the original source links in `DATASETS_AND_LINKS.csv`. Third-party raw archives are not redistributed in this repository because their license and redistribution terms must be respected source by source.

## Main Outputs

- `RESULTS_SUMMARY.md`
- `data_processed/rule_results_model_level.csv`
- `data_processed/rule_results_element_level.csv`
- `data_processed/counterfactual_validation.csv`
- `data_processed/external_ifcopenshell_direct_reference.csv`
- `manuscript/tables/table2_rule_pass_rates.csv`
- `manuscript/tables/table4_counterfactual_validation.csv`

## Citation

If you use this repository, please cite the repository metadata in `CITATION.cff` and cite the original public data sources listed in `DATASETS_AND_LINKS.csv`.

## License

Code in this repository is released under the MIT License. Third-party data sources retain their original licenses and terms.
