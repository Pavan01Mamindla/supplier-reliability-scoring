import json
import hashlib
import pandas as pd
from pathlib import Path
from src.config import REPORTS_DIR, RANDOM_SEED
from scripts.run_pipeline import execute_pipeline

def hash_dataframe(df: pd.DataFrame) -> str:
    cleaned = df.copy()
    for col in cleaned.columns:
        if 'created_at' in col:
            cleaned = cleaned.drop(columns=[col])
    return hashlib.sha256(pd.util.hash_pandas_object(cleaned, index=True).values).hexdigest()

def verify_reproducibility():
    print("Executing Run #1...")
    execute_pipeline(mode="starter", seed=RANDOM_SEED)
    df_run1 = pd.read_csv("data/exports/supplier_scores.csv")
    hash1 = hash_dataframe(df_run1)

    print("Executing Run #2...")
    execute_pipeline(mode="starter", seed=RANDOM_SEED)
    df_run2 = pd.read_csv("data/exports/supplier_scores.csv")
    hash2 = hash_dataframe(df_run2)

    matched = (hash1 == hash2) and (len(df_run1) == len(df_run2))
    report = {
        "status": "PASSED" if matched else "FAILED",
        "random_seed": RANDOM_SEED,
        "run1_sha256": hash1,
        "run2_sha256": hash2,
        "row_count_match": bool(len(df_run1) == len(df_run2)),
        "scores_identical": bool(df_run1['final_score'].equals(df_run2['final_score'])),
        "verified_at": "2026-10-22 12:00:00"
    }

    with open(REPORTS_DIR / "reproducibility_report.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"\nReproducibility Verification Verdict: {report['status']}")
    assert matched, "Deterministic reproducibility failure."

if __name__ == "__main__":
    verify_reproducibility()