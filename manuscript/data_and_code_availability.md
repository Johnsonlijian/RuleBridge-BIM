# Data and Code Availability

This public repository contains the analysis scripts, rule configuration files, generated tables, and generated figures needed to inspect the RuleBridge-BIM pilot results. The pipeline uses open public data from CODE-ACCORD, buildingSMART IDS examples, buildingSMART IFC sample files, and one additional public IFC sample.

Raw third-party archives are not redistributed here. They should be obtained from the original source links in `DATASETS_AND_LINKS.csv` so that each source's license and redistribution terms remain intact.

The analysis can be reproduced with:

```powershell
$env:PYTHONPATH='src'
python scripts\01_build_corpora.py
python scripts\02_run_openbim_checks.py
python scripts\03_make_figures.py
```
