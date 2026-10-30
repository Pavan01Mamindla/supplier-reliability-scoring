import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RANDOM_SEED = int(os.getenv("RANDOM_SEED", 20261022))
DATA_MODE = os.getenv("DATA_MODE", "starter")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DATA_DIR = DATA_DIR / "exports"
GROUND_TRUTH_DIR = DATA_DIR / "ground_truth"

OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"

DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "database/supplier_system.db")

EVALUATION_DATE = "2026-10-22"
EVALUATION_WINDOW = "Trailing 365 Days"
METHODOLOGY_VERSION = "v1.0.0"

SCORING_WEIGHTS = {
    "delivery": 0.25,
    "quality": 0.25,
    "cost": 0.15,
    "capacity": 0.10,
    "compliance": 0.15,
    "risk": 0.10
}

MIN_EVIDENCE_RECORDS = 3

STARTER_COUNTS = {
    "suppliers": 100,
    "purchase_orders": 1000,
    "shipments": 1500,
    "inspections": 2000
}

FULL_COUNTS = {
    "suppliers": 1000,
    "purchase_orders": 10000,
    "shipments": 15000,
    "inspections": 20000
}

for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DATA_DIR, GROUND_TRUTH_DIR, REPORTS_DIR, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)