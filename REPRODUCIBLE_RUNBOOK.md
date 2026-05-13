# Reproducible Runbook

## Environment

Working directory: repository root.

Python environment:

`.venv\Scripts\python.exe`

Installed core packages:

- ifcopenshell
- pandas
- matplotlib
- seaborn
- lxml
- pyyaml

**Headless / CI**：`scripts/03_make_figures.py` 已设置 `matplotlib.use("Agg")`，避免无显示环境下图文件静默不写。

## Optional verification (no IFC)

After tables exist, re-aggregate pass rates from CSVs (stdlib):

```powershell
$env:PYTHONPATH='src'
python scripts\06_reverify_derived_tables.py --md-out rounds/R17_rulebridge_computation_2026-05-13/iter01_reverification.md
```

Writes `outputs/reverification_report.json`.

- `data_raw/CODE-ACCORD-main`
- `data_raw/IDS-development`
- `data_raw/Sample-Test-Files-main`
- `data_raw/AdvancedProject.ifc`

The large archives are kept locally for reproducibility during drafting. Do not redistribute raw archives without checking their licenses.

## Commands

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe scripts\01_build_corpora.py
.\.venv\Scripts\python.exe scripts\02_run_openbim_checks.py
.\.venv\Scripts\python.exe scripts\03_make_figures.py
.\.venv\Scripts\python.exe scripts\04_external_reference_check.py
```

## Generated Tables

- `manuscript/tables/table1_model_inventory.csv`
- `manuscript/tables/table2_rule_pass_rates.csv`
- `manuscript/tables/table3_model_rule_matrix.csv`
- `manuscript/tables/table4_counterfactual_validation.csv`
- `data_processed/external_ifcopenshell_direct_reference.csv`
- `data_processed/external_ifcopenshell_direct_reference_by_model.csv`

## Generated Figures

- `manuscript/figures/figure1_method_workflow.png`
- `manuscript/figures/figure2_code_accord_relations.png`
- `manuscript/figures/figure3_rule_pass_heatmap.png`
- `manuscript/figures/figure4_counterfactual_validation.png`
- `manuscript/figures/figure5_failure_by_theme.png`

## Current Diagnostic Status

The pipeline completed successfully for the reported public-corpus diagnostic outputs.

The empirical pilot supports a bounded evidence-readiness dataset and diagnostic-protocol claim. Higher-confidence journal submission would benefit from at least one of the following additions:

1. a larger corpus of real or permit-like IFC submissions if legally accessible;
2. external expert labelling of the prepared clause-tier sample;
3. comparison against an existing IDS checker, commercial ACC workflow, or transparent manual encoding baseline.
