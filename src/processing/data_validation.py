import json
import pandas as pd
from datetime import datetime
from src.config import REPORTS_DIR

def run_validation_suite(datasets: dict) -> tuple[dict, pd.DataFrame]:
    checks = []
    
    # 1. Primary Key Uniqueness
    for entity, df in datasets.items():
        if df.empty or 'ground_truth' in entity:
            continue
        pk = df.columns[0]
        dupes = df[pk].duplicated().sum()
        checks.append({
            'check_name': f"PK_UNIQUENESS_{entity.upper()}",
            'status': 'PASS' if dupes == 0 else 'FAIL',
            'severity': 'CRITICAL',
            'failures_count': int(dupes),
            'description': f"Primary key column {pk} uniqueness verification in table {entity}."
        })

    # 2. Foreign Key Integrity: Shipments -> PO
    po_ids = set(datasets['purchase_orders']['po_id'])
    invalid_po_shps = datasets['shipments'][~datasets['shipments']['po_id'].isin(po_ids)]
    checks.append({
        'check_name': 'FK_SHIPMENT_PURCHASE_ORDER',
        'status': 'PASS' if len(invalid_po_shps) == 0 else 'FAIL',
        'severity': 'HIGH',
        'failures_count': len(invalid_po_shps),
        'description': f"Detected {len(invalid_po_shps)} shipments referencing invalid PO IDs."
    })

    # 3. Date Ordering: Dispatch <= Delivery
    merged_del = datasets['delivery_events'].merge(datasets['shipments'], on='shipment_id', suffixes=('_del', '_shp'))
    invalid_dates = []
    for _, r in merged_del.iterrows():
        try:
            if datetime.strptime(r['actual_delivery_date'], '%Y-%m-%d') < datetime.strptime(r['dispatch_date'], '%Y-%m-%d'):
                invalid_dates.append(r['delivery_id'])
        except Exception:
            invalid_dates.append(r['delivery_id'])

    checks.append({
        'check_name': 'DATE_ORDER_DISPATCH_DELIVERY',
        'status': 'PASS' if len(invalid_dates) == 0 else 'FAIL',
        'severity': 'HIGH',
        'failures_count': len(invalid_dates),
        'description': f"Found {len(invalid_dates)} deliveries occurring before dispatch date."
    })

    # 4. Mandatory Provenance in Risk Signals
    null_source = datasets['risk_signals']['source'].isnull().sum()
    null_created = datasets['risk_signals']['created_at'].isnull().sum()
    total_prov_failures = int(null_source + null_created)
    checks.append({
        'check_name': 'RISK_SIGNAL_PROVENANCE',
        'status': 'PASS' if total_prov_failures == 0 else 'FAIL',
        'severity': 'MEDIUM',
        'failures_count': total_prov_failures,
        'description': f"Identified {total_prov_failures} risk signals missing origin source or timestamp."
    })

    # 5. Future Data Leakage
    eval_cutoff = datetime(2026, 10, 22)
    future_signals = 0
    for _, r in datasets['risk_signals'].iterrows():
        if r.get('event_date'):
            try:
                if datetime.strptime(r['event_date'], '%Y-%m-%d') > eval_cutoff:
                    future_signals += 1
            except Exception:
                pass

    checks.append({
        'check_name': 'TEMPORAL_FUTURE_LEAKAGE',
        'status': 'PASS' if future_signals == 0 else 'FAIL',
        'severity': 'HIGH',
        'failures_count': future_signals,
        'description': f"Detected {future_signals} records with timestamps past evaluation cutoff (2026-10-22)."
    })

    df_checks = pd.DataFrame(checks)
    total_checks = len(df_checks)
    passed_checks = len(df_checks[df_checks['status'] == 'PASS'])
    failed_checks = len(df_checks[df_checks['status'] == 'FAIL'])

    summary = {
        'total_checks_executed': total_checks,
        'passed_checks': passed_checks,
        'failed_checks': failed_checks,
        'overall_status': 'UNHEALTHY' if failed_checks > 0 else 'HEALTHY',
        'execution_timestamp': '2026-10-22 12:00:00'
    }

    # Persist Reports
    report_json = {
        'summary': summary,
        'checks': checks
    }
    with open(REPORTS_DIR / "validation_report.json", "w") as f:
        json.dump(report_json, f, indent=4)
        
    df_checks.to_csv(REPORTS_DIR / "validation_report.csv", index=False)

    return summary, df_checks