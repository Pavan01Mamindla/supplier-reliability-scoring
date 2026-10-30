import pandas as pd
from datetime import datetime, timedelta

def inject_anomalies(df_shipments, df_delivery_events, df_risk_signals, df_sites, df_suppliers):
    ground_truth = []

    # 1. Orphan Shipment
    if len(df_shipments) > 0:
        orphan_idx = 0
        original_po = df_shipments.at[orphan_idx, 'po_id']
        anomalous_po = "PO-2026-999999"
        df_shipments.at[orphan_idx, 'po_id'] = anomalous_po
        ground_truth.append({
            'issue_type': 'ORPHAN_SHIPMENT',
            'ground_truth_label': 'INVALID_FOREIGN_KEY',
            'affected_record_id': df_shipments.at[orphan_idx, 'shipment_id'],
            'expected_validation_result': 'FAIL',
            'anomaly_description': f"Shipment references non-existent PO {anomalous_po}."
        })

    # 2. Date Inversion (Delivery before Dispatch)
    if len(df_delivery_events) > 1 and len(df_shipments) > 1:
        inv_idx = 1
        dispatch_str = df_shipments.at[inv_idx, 'dispatch_date']
        dispatch_dt = datetime.strptime(dispatch_str, '%Y-%m-%d')
        inverted_delivery = dispatch_dt - timedelta(days=5)
        df_delivery_events.at[inv_idx, 'actual_delivery_date'] = inverted_delivery.strftime('%Y-%m-%d')
        df_delivery_events.at[inv_idx, 'delivery_status'] = 'Early'
        ground_truth.append({
            'issue_type': 'DATE_INVERSION',
            'ground_truth_label': 'TEMPORAL_VIOLATION',
            'affected_record_id': df_delivery_events.at[inv_idx, 'delivery_id'],
            'expected_validation_result': 'FAIL',
            'anomaly_description': f"Delivery date {inverted_delivery.strftime('%Y-%m-%d')} occurs prior to dispatch date {dispatch_str}."
        })

    # 3. Future Data Leakage / Future Cutoff Signal
    fut_sig_id = "RSK-FUTURE-SIGNAL-01"
    future_record = {
        'signal_id': fut_sig_id,
        'supplier_id': df_suppliers.iloc[0]['supplier_id'],
        'event_date': '2027-06-15',
        'source': 'Forecast Engine',
        'severity': 8.5,
        'description': 'Predicted labor disruption in 2027',
        'recovery_status': 'Active',
        'created_at': '2027-06-15 00:00:00'
    }
    df_risk_signals = pd.concat([df_risk_signals, pd.DataFrame([future_record])], ignore_index=True)
    ground_truth.append({
        'issue_type': 'FUTURE_DATA_LEAKAGE',
        'ground_truth_label': 'FUTURE_DATE_VIOLATION',
        'affected_record_id': fut_sig_id,
        'expected_validation_result': 'FAIL',
        'anomaly_description': 'Event timestamp occurs in future (2027-06-15) relative to evaluation date (2026-10-22).'
    })

    # 4. Missing Source and Timestamp
    missing_sig_id = "RSK-ANOM-MISSING-01"
    missing_record = {
        'signal_id': missing_sig_id,
        'supplier_id': df_suppliers.iloc[1]['supplier_id'],
        'event_date': '2026-03-01',
        'source': None,
        'severity': 7.0,
        'description': 'Unattributed risk signal',
        'recovery_status': 'Active',
        'created_at': None
    }
    df_risk_signals = pd.concat([df_risk_signals, pd.DataFrame([missing_record])], ignore_index=True)
    ground_truth.append({
        'issue_type': 'MISSING_MANDATORY_PROVENANCE',
        'ground_truth_label': 'NULL_METADATA_VIOLATION',
        'affected_record_id': missing_sig_id,
        'expected_validation_result': 'FAIL',
        'anomaly_description': 'Risk signal record missing mandatory source provenance and created_at audit timestamp.'
    })

    # 5. Site Conflation
    if len(df_sites) > 2 and len(df_suppliers) > 2:
        conflate_idx = 2
        source_sup = df_sites.at[conflate_idx, 'supplier_id']
        alien_sup = df_suppliers.iloc[-1]['supplier_id']
        df_sites.at[conflate_idx, 'supplier_id'] = alien_sup
        ground_truth.append({
            'issue_type': 'SITE_CONFLATION',
            'ground_truth_label': 'CROSS_SUPPLIER_MISMATCH',
            'affected_record_id': df_sites.at[conflate_idx, 'site_id'],
            'expected_validation_result': 'FAIL',
            'anomaly_description': f"Site ID naming structure mismatches parent foreign key assignment ({alien_sup})."
        })

    df_ground_truth = pd.DataFrame(ground_truth)
    return df_shipments, df_delivery_events, df_risk_signals, df_sites, df_ground_truth

    