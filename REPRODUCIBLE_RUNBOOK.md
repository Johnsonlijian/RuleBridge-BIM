# Reproducible Runbook

## Environment

Working directory: repository root.

Python environment:

`.venv\Scripts\python.exe`

Installed core packages:

- ifcopenshell
- ifctester
- pandas
- matplotlib
- seaborn
- lxml
- pyyaml

Headless/CI note: `scripts/03_make_figures.py` uses `matplotlib.use("Agg")` so figures can be generated without a desktop display.

## Data Already Downloaded

- `data_raw/CODE-ACCORD-main`
- `data_raw/IDS-development`
- `data_raw/Sample-Test-Files-main`
- `data_raw/AdvancedProject.ifc`

The large archives are kept locally for reproducibility during drafting. Do not redistribute raw archives without checking their licenses. Public outputs use source-relative labels rather than local absolute paths.

## Commands

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe scripts\01_build_corpora.py
.\.venv\Scripts\python.exe scripts\02_run_openbim_checks.py
.\.venv\Scripts\python.exe scripts\04_external_reference_check.py
.\.venv\Scripts\python.exe scripts\07_expanded_corpus_stats.py
.\.venv\Scripts\python.exe scripts\08_ifctester_reference.py
.\.venv\Scripts\python.exe scripts\09_evidence_route_graph_and_triage.py
.\.venv\Scripts\python.exe scripts\10_mutation_repair_simulation.py
.\.venv\Scripts\python.exe scripts\03_make_figures.py
```

## Optional Verification Without Re-reading IFC

After tables exist, re-aggregate pass rates from CSVs:

```powershell
$env:PYTHONPATH='src'
python scripts\06_reverify_derived_tables.py --md-out rounds/R17_rulebridge_computation_2026-05-13/iter01_reverification.md
```

This writes `outputs/reverification_report.json` with per-rule aggregate pass rates, descriptive mean model pass rates and model/element-level consistency checks.

## Generated Tables

- `manuscript/tables/table1_model_inventory.csv`
- `manuscript/tables/table2_rule_pass_rates.csv`
- `manuscript/tables/table3_model_rule_matrix.csv`
- `manuscript/tables/table4_counterfactual_validation.csv`
- `manuscript/tables/table5_expanded_corpus_strata.csv`
- `manuscript/tables/table6_cluster_bootstrap_intervals.csv`
- `manuscript/tables/table7_ids_rulebridge_tool_agreement.csv`
- `manuscript/tables/table8_ifctester_reference_summary.csv`
- `manuscript/tables/table9_evidence_route_graph_summary.csv`
- `manuscript/tables/table10_project_delivery_triage_simulation.csv`
- `manuscript/tables/table11_mutation_repair_operator_summary.csv`

## Generated Data Outputs

- `data_processed/ifc_model_inventory.csv`
- `data_processed/rule_results_model_level.csv`
- `data_processed/rule_results_element_level.csv`
- `data_processed/external_ifcopenshell_direct_reference.csv`
- `data_processed/external_ifcopenshell_direct_reference_by_model.csv`
- `data_processed/corpus_manifest_strata.csv`
- `data_processed/readiness_by_corpus_stratum.csv`
- `data_processed/readiness_by_source_schema.csv`
- `data_processed/cluster_bootstrap_intervals.csv`
- `data_processed/ifctester_reference_summary.csv`
- `data_processed/ids_rulebridge_tool_agreement.csv`
- `data_processed/evidence_route_graph_summary.csv`
- `data_processed/project_delivery_triage_simulation.csv`
- `data_processed/mutation_repair_operator_summary.csv`

## Generated Figures

- `manuscript/figures/figure1_method_workflow.png`
- `manuscript/figures/figure2_code_accord_relations.png`
- `manuscript/figures/figure3_rule_pass_heatmap.png`
- `manuscript/figures/figure4_counterfactual_validation.png`
- `manuscript/figures/figure5_failure_by_theme.png`

## Current Diagnostic Status

The expanded public-corpus diagnostic completed successfully for 344 discovered public/local-inspection IFC files, of which 341 parsed successfully. The current package supports a bounded evidence-readiness benchmark, an IfcOpenShell direct-field reference, an IDS/IfcTester reference for IDS-expressible checks, evidence-route graph summaries, computational project-delivery triage outputs and evidence-mutation/repair sensitivity checks.

The package still does not claim legal compliance, permit-submission representativeness, independent expert validation, or superiority over commercial ACC tools. Higher-confidence journal submission would still benefit from real permit-like IFC submissions, external expert labelling, or a commercial ACC/manual-encoding comparison if those resources become available.
