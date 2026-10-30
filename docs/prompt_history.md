# Complete Prompt & Interaction History

**Project:** Supplier Reliability Scoring System  
**Candidate:** Pavan Mamindla  
**Repository:** https://github.com/Pavan01Mamindla/supplier-reliability-scoring  

---

### Prompt 1: Initial Architecture & Complete System Specification
- **User Prompt:** Provided full master prompt detailing the end-to-end assignment (11 relational entities, 6-dimension scoring formula, synthetic data generation, 5 labeled anomalies, FastAPI REST API, Streamlit dashboard, automated pytest suite, Windows setup guide, and GitHub submission instructions).
- **AI Contribution:** Produced modular project structure, SQLite schema (`database/schema.sql`), generator scripts (`src/generators/`), scoring engines (`src/scoring/`), Streamlit UI (`dashboard/app.py`), and FastAPI routes (`src/api/main.py`).

---

### Prompt 2: Local Environment Setup & Dependency Installation
- **User Action:** Initialized virtual environment on Windows 11 with PowerShell:
  ```powershell
  python -m venv venv
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
