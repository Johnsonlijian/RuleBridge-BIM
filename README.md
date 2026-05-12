# RuleBridge-BIM

RuleBridge-BIM is a reproducible OpenBIM information-readiness benchmark for automated compliance checking (ACC). The project links regulatory relation labels, IDS-like information requirements, deterministic IFC evidence extraction, and counterfactual rule-sensitivity checks.

This repository is prepared as the public reproducibility package for the manuscript project. It is not a public dump of the full submission workspace: raw third-party archives, active submission drafts, reviewer strategy notes, and journal-specific packages are intentionally excluded.

## What the Benchmark Does

The pipeline:

1. builds a public artifact registry from CODE-ACCORD, buildingSMART IDS examples, and public IFC sample sources;
2. maps regulatory relation labels into bounded machine-checkability tiers;
3. expresses selected information needs as IDS-like evidence requirements;
4. extracts IFC evidence deterministically;
5. reports readiness results for ten evidence-oriented checks;
6. tests checker sensitivity with counterfactual pass/fail mutations.

The benchmark does not claim legal compliance of sampled buildings, does not claim that the IFC samples represent permit submissions, and does not use a language model to produce final compliance verdicts.

## Current Empirical Scope

- 4,329 annotated CODE-ACCORD relation pairs.
- 315 direct numeric regulatory relations.
- 3,002 semantic precondition relations.
- 12 public IDS example files.
- 38 IDS specifications and 226 IDS facets.
- 24 public IFC models across IFC2X3, IFC4, and IFC4X3.
- 2,937 applicable `IfcElement` targets.
- 10 OpenBIM information-readiness checks.
- 141 counterfactual validation rows.

## Repository Layout

```text
configs/                Configuration files used by the benchmark scripts
data_processed/         Derived tables generated from public inputs
manuscript/figures/     Generated figures for reporting
manuscript/tables/      Generated reporting tables
scripts/                Reproducible pipeline scripts
src/                    Python package code
DATASETS_AND_LINKS.csv  Public source registry
RESULTS_SUMMARY.md      Compact empirical summary
REPRODUCIBLE_RUNBOOK.md Reproduction notes
```

Excluded local folders include `data_raw/`, `data_interim/`, `Submit-AIC-2026/`, `rounds/`, `logs/`, and active submission manuscripts.

## Reproduce

Create an environment with the dependencies in `pyproject.toml`, then run:

```powershell
$env:PYTHONPATH='src'
python scripts\01_build_corpora.py
python scripts\02_run_openbim_checks.py
python scripts\03_make_figures.py
```

Raw public data should be obtained from the original source links in `DATASETS_AND_LINKS.csv`. Third-party raw archives are not redistributed in this repository because their license and redistribution terms must be respected source by source.

## Main Outputs

- `RESULTS_SUMMARY.md`
- `data_processed/rule_results_model_level.csv`
- `data_processed/rule_results_element_level.csv`
- `data_processed/counterfactual_validation.csv`
- `manuscript/tables/table2_rule_pass_rates.csv`
- `manuscript/tables/table4_counterfactual_validation.csv`

## Citation

If you use this repository, please cite the repository metadata in `CITATION.cff` and cite the original public data sources listed in `DATASETS_AND_LINKS.csv`.

## License

Code in this repository is released under the MIT License. Third-party data sources retain their original licenses and terms.
