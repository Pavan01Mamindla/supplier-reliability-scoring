# LLM Usage & Transparency Disclosure

In compliance with the YottaFlex AI Candidate Submission Guidelines, this document outlines how AI tools were utilized during the development of this project.

## 1. AI Acceleration (Where LLMs Helped)
- **Scaffolding & Architecture**: Generated boilerplate templates for the 11 relational entities, database schema (`schema.sql`), and FastAPI route scaffolding.
- **Data Generation Logic**: Accelerated writing synthetic data generator functions for master and event data using NumPy and Pandas.
- **Interactive UI Layout**: Accelerated UI code generation for Streamlit and Plotly radar/pie charts.

## 2. Human Review, Diagnostics & Custom Validation (What I Personally Fixed)
During local execution on Windows with Python 3.14, several critical runtime and logic issues were identified, diagnosed, and resolved manually:
- **Module Resolution (`PYTHONPATH`)**: Fixed `ModuleNotFoundError: No module named 'src'` by configuring execution paths properly in PowerShell and Python runners.
- **Relational Constraint Conflicts on Edge Cases**: SQLite foreign key constraints and `NOT NULL` rules originally blocked deliberate anomaly ingestion. Adjusted table definitions (`risk_signals.source`, `risk_signals.created_at`) to be nullable and staged data with `PRAGMA foreign_keys = OFF` during initial synthetic data ingestion.
- **Missing Timestamp Columns**: Resolved `sqlite3.IntegrityError: NOT NULL constraint failed: supplier_scores.created_at` by adding explicit audit timestamps to evaluation scores.
- **Missing Column Defensive Guards in Scoring**: Pytest identified an issue where empty DataFrames raised `KeyError: 'supplier_id'`. Implemented defensive filtering (`_filter_df`) in `src/scoring/supplier_score.py` to gracefully handle sparse and empty data.
- **Test Client Dependency Configuration**: Installed and configured `httpx` and `httpx2` to support Starlette/FastAPI's test client on Python 3.14.

## 3. Prompt History
- The complete transcript of development prompts, error traces, and iterative fixes is preserved and submitted alongside this repository in `docs/prompt_history.md`.