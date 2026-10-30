import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from src.config import DATABASE_PATH, REPORTS_DIR

app = FastAPI(
    title="Supplier Reliability Scoring System API",
    version="1.0.0",
    description="Enterprise REST endpoints for querying supplier metrics, evaluation dimensions, and detected pipeline anomalies."
)

def get_db_connection():
    if not DATABASE_PATH.exists():
        raise HTTPException(status_code=500, detail="Database file not initialized. Run pipeline first.")
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "UP",
        "database_connected": DATABASE_PATH.exists(),
        "api_version": "1.0.0"
    }

@app.get("/suppliers", tags=["Suppliers"])
def get_suppliers(limit: int = 50, offset: int = 0):
    conn = get_db_connection()
    df = pd.read_sql_query(f"SELECT * FROM suppliers LIMIT {limit} OFFSET {offset}", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/suppliers/{supplier_id}", tags=["Suppliers"])
def get_supplier_by_id(supplier_id: str):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM suppliers WHERE supplier_id = ?", conn, params=(supplier_id,))
    conn.close()
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found.")
    return df.iloc[0].to_dict()

@app.get("/suppliers/{supplier_id}/score", tags=["Scoring"])
def get_supplier_score(supplier_id: str):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM supplier_scores WHERE supplier_id = ?", conn, params=(supplier_id,))
    conn.close()
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Score record for {supplier_id} not found.")
    return df.iloc[0].to_dict()

@app.get("/suppliers/{supplier_id}/history", tags=["Scoring"])
def get_supplier_history(supplier_id: str):
    conn = get_db_connection()
    df_pos = pd.read_sql_query("SELECT * FROM purchase_orders WHERE supplier_id = ?", conn, params=(supplier_id,))
    df_shp = pd.read_sql_query("SELECT * FROM shipments WHERE supplier_id = ?", conn, params=(supplier_id,))
    conn.close()
    return {
        "supplier_id": supplier_id,
        "total_purchase_orders": len(df_pos),
        "total_shipments": len(df_shp),
        "purchase_orders": df_pos.to_dict(orient="records"),
        "shipments": df_shp.to_dict(orient="records")
    }

@app.get("/scores", tags=["Scoring"])
def get_all_scores(classification: str = None):
    conn = get_db_connection()
    query = "SELECT * FROM supplier_scores"
    params = ()
    if classification:
        query += " WHERE classification = ?"
        params = (classification,)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/risks", tags=["Risk Management"])
def get_risk_signals():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM risk_signals ORDER BY severity DESC", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/anomalies", tags=["Quality & Validation"])
def get_anomalies():
    gt_path = DATABASE_PATH.parent.parent / "data" / "ground_truth" / "ground_truth.json"
    if not gt_path.exists():
        raise HTTPException(status_code=404, detail="Ground truth anomaly record not found.")
    import json
    with open(gt_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/metrics", tags=["Analytics"])
def get_executive_metrics():
    conn = get_db_connection()
    scores = pd.read_sql_query("SELECT * FROM supplier_scores", conn)
    conn.close()
    if scores.empty:
        return {"message": "No scores generated yet."}
    return {
        "total_suppliers_evaluated": len(scores),
        "average_score": round(scores['final_score'].mean(), 2),
        "classification_breakdown": scores['classification'].value_counts().to_dict(),
        "unrated_count": int((scores['classification'] == 'Unrated').sum())
    }

@app.get("/validation-report", tags=["Quality & Validation"])
def get_validation_report():
    report_file = REPORTS_DIR / "validation_report.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Validation report has not been generated.")
    import json
    with open(report_file, "r") as f:
        data = json.load(f)
    return data