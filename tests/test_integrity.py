import pytest
import sqlite3
import pandas as pd
from pathlib import Path
from src.config import DATABASE_PATH

def test_primary_key_uniqueness():
    if not DATABASE_PATH.exists():
        pytest.skip("Database not populated.")
    conn = sqlite3.connect(DATABASE_PATH)
    for table in ['suppliers', 'sites', 'purchase_orders', 'shipments', 'invoices']:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        pk = df.columns[0]
        assert df[pk].duplicated().sum() == 0
    conn.close()

def test_ground_truth_isolation():
    gt_file = Path("data/ground_truth/ground_truth.csv")
    assert gt_file.exists()
    df_gt = pd.read_csv(gt_file)
    assert len(df_gt) >= 5
    assert "issue_type" in df_gt.columns