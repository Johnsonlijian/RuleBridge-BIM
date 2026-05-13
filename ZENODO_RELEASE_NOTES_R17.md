# Zenodo release notes for ECAM submission

Recommended GitHub release tag: `v1.0.0-ecam-r17`

Recommended archive title:

RuleBridge-BIM: reproducible OpenBIM diagnostic protocol for pre-compliance information readiness

Recommended archive description:

This archive contains the public reproducibility package for the RuleBridge-BIM manuscript. It includes scripts, rule configuration files, generated diagnostic tables, generated figures, a source registry and reproducibility runbook for an OpenBIM pre-compliance information-readiness diagnostic protocol. Raw third-party IFC/IDS/CODE-ACCORD archives are not redistributed; users should obtain them from the original sources listed in `DATASETS_AND_LINKS.csv`.

Files to include:

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `DATASETS_AND_LINKS.csv`
- `REPRODUCIBLE_RUNBOOK.md`
- `RESULTS_SUMMARY.md`
- `configs/`
- `scripts/`
- `src/`
- `data_processed/`
- `manuscript/figures/`
- `manuscript/tables/`
- `pyproject.toml`
- `uv.lock`

Files to exclude:

- `data_raw/`
- `data_interim/`
- `Submit-AIC-2026/`
- `rounds/`
- `logs/`
- `deliverables/`
- active manuscript drafts, cover letters, title pages and reviewer-strategy files

Data availability text after DOI is minted:

The reproducibility package, scripts, rule configurations, processed diagnostic tables and generated figures are archived at Zenodo: `[DOI to be inserted]`. The active public code repository is available at https://github.com/Johnsonlijian/RuleBridge-BIM. Raw third-party IFC, IDS and regulatory-data archives are not redistributed and should be obtained from the original sources listed in the source registry.

Human-only action:

Create or connect the Zenodo archive from the GitHub release, mint the DOI, then replace `[DOI to be inserted]` in the final title page, main manuscript and cover letter if required by the journal.
