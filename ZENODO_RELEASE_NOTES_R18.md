# Zenodo Release Notes R18

Suggested release tag: `v1.0.0-ecam-r18`

## Purpose

This release archives the public reproducibility package for the ECAM-oriented RuleBridge-BIM R18 manuscript. It upgrades the earlier pilot package into an expanded public OpenBIM evidence-route benchmark for pre-compliance information governance in construction project delivery.

## Main Changes Since R17

- Expanded public IFC discovery from 24 pilot models to 344 discovered IFC files, with 341 files parsed successfully.
- Added corpus stratification by source, schema, model type and completeness tier.
- Added model/evidence-family readiness summaries and cluster-bootstrap uncertainty outputs.
- Added an IDS/IfcTester reference for the IDS-expressible subset of RuleBridge-BIM checks.
- Added RuleBridge-BIM vs IfcTester agreement/disagreement outputs.
- Added Evidence Route Graph summaries with route tiers and project-delivery triage states.
- Added synthetic mutation/repair sensitivity outputs for deterministic evidence-route checks.
- Updated generated figures and reporting tables for the ECAM R18 framing.

## Included Public Assets

- `configs/`
- `configs/ids_reference/rulebridge_ifctester_reference.ids`
- `src/`
- `scripts/`
- `data_processed/`
- `manuscript/figures/`
- `manuscript/tables/`
- `README.md`
- `REPRODUCIBLE_RUNBOOK.md`
- `RESULTS_SUMMARY.md`
- `DATASETS_AND_LINKS.csv`
- `CITATION.cff`
- `LICENSE`

## Excluded Assets

Raw third-party IFC/IDS/CODE-ACCORD archives are not redistributed. Active submission manuscripts, title pages, cover letters, reviewer strategy notes, internal rounds, logs, local deliverables and private author/funding material are excluded from the public release.

## DOI Placeholder

Zenodo DOI: `[DOI to be inserted after release minting]`

After minting the DOI, update the manuscript data availability statement and `CITATION.cff` if required by the journal workflow.
