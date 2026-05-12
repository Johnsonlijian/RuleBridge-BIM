# Reproducible Runbook

## Environment

Working directory:

`R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-CodexNature\AIC_Paper_Automated_Construction_2026`

Python environment:

`.venv\Scripts\python.exe`

Installed core packages:

- ifcopenshell
- pandas
- matplotlib
- seaborn
- lxml
- pyyaml

## Data Already Downloaded

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
```

## Generated Tables

- `manuscript/tables/table1_model_inventory.csv`
- `manuscript/tables/table2_rule_pass_rates.csv`
- `manuscript/tables/table3_model_rule_matrix.csv`
- `manuscript/tables/table4_counterfactual_validation.csv`

## Generated Figures

- `manuscript/figures/figure1_method_workflow.png`
- `manuscript/figures/figure2_code_accord_relations.png`
- `manuscript/figures/figure3_rule_pass_heatmap.png`
- `manuscript/figures/figure4_counterfactual_validation.png`
- `manuscript/figures/figure5_failure_by_theme.png`

## Current Validation Status

The pipeline completed successfully on 2026-04-29.

The empirical pilot is suitable for a strong methods paper draft. Before journal submission, the work should add at least one of the following:

1. a larger corpus of real design-stage IFC submissions if accessible;
2. expert validation of the rule-template mapping;
3. live LLM runs against the prompt pack with model/version logging;
4. comparison against an existing IDS checker or ACC tool.

