# Project Engineering & Architectural Reasoning

## 1. Problem & Context
Evaluating supplier reliability is often flawed because organizations either treat missing data as good performance or rely on opaque machine-learning models that procurement teams cannot explain. This project addresses both issues through an explainable, deterministic 6-dimension scoring framework.

## 2. Key Architectural Decisions & Trade-offs
- **SQLite over External RDBMS (PostgreSQL/MySQL)**:
  - *Decision*: Use local SQLite3.
  - *Reasoning*: Zero setup friction on any developer machine (no Docker or cloud accounts required) while retaining standard SQL syntax, foreign keys, and fast query execution.
- **Explicit Scoring Math vs. Machine Learning**:
  - *Decision*: Clamped, weighted scoring functions ($S_{\text{del}}$, $S_{\text{qual}}$, etc.).
  - *Reasoning*: Procurement audits require transparent numerators and denominators. If a supplier score drops from 85 to 62, analysts can trace the drop directly to specific delivery delays or invoice disputes.
- **Ground Truth Isolation**:
  - *Decision*: Store anomalies separately in `data/ground_truth/` rather than marking them with feature flags in the operational tables.
  - *Reasoning*: Prevents data leakage into scoring calculations while enabling independent QA validation checks.

## 3. Assumptions & Edge-Case Handling
- **Minimum Evidence Requirement**: Any supplier with fewer than 3 purchase orders is categorized as `Unrated` rather than assigned an arbitrary default score.
- **Point-in-Time Temporal Boundary**: All scoring runs use an explicit evaluation cutoff date (`2026-10-22`). Future records are rejected to simulate realistic operational reporting.

## 4. Verification & Validation Strategy
- **Automated Tests**: Pytest suite validates perfect scores, penalty bounds, defensive empty-dataset slicing, and API endpoints.
- **Cryptographic Reproducibility**: Seed `20261022` produces identical SHA-256 data hashes across multiple runs, as verified by `scripts/reproduce_check.py`.

## 5. Known Limitations
- The synthetic dataset models 1,000 suppliers and 10,000 orders in memory using Pandas; scaling beyond 100,000 suppliers would require batch streaming or SQL-level aggregations.