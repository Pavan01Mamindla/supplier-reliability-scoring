import sys
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
import pandas as pd
from src.config import (
    DATA_MODE, STARTER_COUNTS, FULL_COUNTS, RANDOM_SEED,
    RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DATA_DIR, GROUND_TRUTH_DIR,
    DATABASE_PATH, DATABASE_DIR
)
from src.generators.master_data import generate_suppliers_and_sites
from src.generators.transaction_data import generate_purchase_orders_and_lines
from src.generators.event_data import generate_events
from src.generators.anomaly_generator import inject_anomalies
from src.scoring.supplier_score import evaluate_supplier
from src.processing.data_validation import run_validation_suite

def execute_pipeline(mode: str = "starter", seed: int = RANDOM_SEED):
    print(f"\n[1/7] Initializing Synthetic Generation (Mode: {mode}, Seed: {seed})...")
    counts = STARTER_COUNTS if mode == "starter" else FULL_COUNTS

    # 1. Master Data
    df_suppliers, df_sites, df_contracts = generate_suppliers_and_sites(counts['suppliers'], seed)

    # 2. Transactions
    df_pos, df_po_lines = generate_purchase_orders_and_lines(
        df_suppliers, df_sites, df_contracts, counts['purchase_orders'], seed
    )

    # 3. Events
    df_shipments, df_deliveries, df_inspections, df_invoices, df_risks = generate_events(
        df_pos, df_suppliers, counts['shipments'], counts['inspections'], seed
    )

    # 4. Inject Labelled Anomalies
    print("[2/7] Injecting Deterministic Edge Cases & Anomalies...")
    df_shipments, df_deliveries, df_risks, df_sites, df_ground_truth = inject_anomalies(
        df_shipments, df_deliveries, df_risks, df_sites, df_suppliers
    )

    # Store Ground Truth
    df_ground_truth.to_csv(GROUND_TRUTH_DIR / "ground_truth.csv", index=False)
    df_ground_truth.to_json(GROUND_TRUTH_DIR / "ground_truth.json", orient="records", indent=4)

    raw_datasets = {
        'suppliers': df_suppliers,
        'sites': df_sites,
        'contracts': df_contracts,
        'purchase_orders': df_pos,
        'po_lines': df_po_lines,
        'shipments': df_shipments,
        'delivery_events': df_deliveries,
        'inspections': df_inspections,
        'invoices': df_invoices,
        'risk_signals': df_risks
    }

    # Save CSVs & JSONs
    print("[3/7] Exporting Datasets to CSV and JSON Storage...")
    for name, df in raw_datasets.items():
        df.to_csv(RAW_DATA_DIR / f"{name}.csv", index=False)
        df.to_csv(EXPORTS_DATA_DIR / f"{name}.csv", index=False)
        df.to_json(EXPORTS_DATA_DIR / f"{name}.json", orient="records", indent=2)

    # 5. Scoring Engine Execution
    print("[4/7] Running Multi-Dimensional Reliability Scoring...")
    score_records = []
    for sup_id in df_suppliers['supplier_id']:
        score_dict = evaluate_supplier(sup_id, raw_datasets)
        score_records.append(score_dict)

    df_scores = pd.DataFrame(score_records)
    df_scores.to_csv(PROCESSED_DATA_DIR / "supplier_scores.csv", index=False)
    df_scores.to_csv(EXPORTS_DATA_DIR / "supplier_scores.csv", index=False)
    raw_datasets['supplier_scores'] = df_scores

    # 6. Database Hydration
    print("[5/7] Initializing SQLite Relational Database & Persisting Records...")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    schema_path = DATABASE_DIR / "schema.sql"
    with open(schema_path, "r") as f:
        conn.executescript(f.read())

    conn.execute("PRAGMA foreign_keys = OFF;")

    for table_name, df in raw_datasets.items():
        df.to_sql(table_name, conn, if_exists="append", index=False)
    
    conn.commit()
    conn.close()

    # 7. Validation Execution
    print("[6/7] Executing Automated Validation Checks & Logging Diagnostics...")
    summary, _ = run_validation_suite(raw_datasets)

    print(f"[7/7] Pipeline Complete! Evaluated {len(df_suppliers)} suppliers across {len(df_pos)} POs.\n")
    return summary

if __name__ == "__main__":
    execute_pipeline(mode="starter")