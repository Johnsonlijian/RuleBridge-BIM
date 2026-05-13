# Data and Code Availability

The public reproducibility package for this study is available at:

https://github.com/Johnsonlijian/RuleBridge-BIM

The repository contains the analysis scripts, rule configuration files, generated tables, generated figures, IDS/IfcTester reference files and source registry used to inspect the reported benchmark results. Raw third-party archives are not redistributed in the repository; they should be obtained from the original sources listed in `DATASETS_AND_LINKS.csv` so that each source's license and redistribution terms remain intact.

The analysis can be reproduced with:

```powershell
$env:PYTHONPATH='src'
python scripts\01_build_corpora.py
python scripts\02_run_openbim_checks.py
python scripts\04_external_reference_check.py
python scripts\07_expanded_corpus_stats.py
python scripts\08_ifctester_reference.py
python scripts\09_evidence_route_graph_and_triage.py
python scripts\10_mutation_repair_simulation.py
python scripts\03_make_figures.py
```
