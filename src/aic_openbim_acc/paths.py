from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIGS = ROOT / "configs"
DATA_RAW = ROOT / "data_raw"
DATA_INTERIM = ROOT / "data_interim"
DATA_PROCESSED = ROOT / "data_processed"
MANUSCRIPT = ROOT / "manuscript"
TABLES = MANUSCRIPT / "tables"
FIGURES = MANUSCRIPT / "figures"
OUTPUTS = ROOT / "outputs"


def ensure_dirs() -> None:
    for path in [CONFIGS, DATA_RAW, DATA_INTERIM, DATA_PROCESSED, MANUSCRIPT, TABLES, FIGURES, OUTPUTS]:
        path.mkdir(parents=True, exist_ok=True)

