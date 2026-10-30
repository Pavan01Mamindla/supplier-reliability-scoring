import pandas as pd
from src.config import SCORING_WEIGHTS, EVALUATION_DATE, EVALUATION_WINDOW, METHODOLOGY_VERSION, MIN_EVIDENCE_RECORDS
from src.scoring.delivery_score import calculate_delivery_score
from src.scoring.quality_score import calculate_quality_score
from src.scoring.cost_score import calculate_cost_score
from src.scoring.capacity_score import calculate_capacity_score
from src.scoring.compliance_score import calculate_compliance_score
from src.scoring.risk_score import calculate_risk_score

def evaluate_supplier(supplier_id: str, datasets: dict) -> dict:
    def _filter_df(df, col, val):
        if df is None or df.empty or col not in df.columns:
            return pd.DataFrame()
        return df[df[col] == val]

    df_sites = _filter_df(datasets.get('sites'), 'supplier_id', supplier_id)
    df_contracts = _filter_df(datasets.get('contracts'), 'supplier_id', supplier_id)
    df_pos = _filter_df(datasets.get('purchase_orders'), 'supplier_id', supplier_id)
    df_shp = _filter_df(datasets.get('shipments'), 'supplier_id', supplier_id)

    shp_ids = df_shp['shipment_id'].tolist() if not df_shp.empty and 'shipment_id' in df_shp.columns else []
    
    raw_del = datasets.get('delivery_events')
    if raw_del is not None and not raw_del.empty and 'shipment_id' in raw_del.columns:
        df_del = raw_del[raw_del['shipment_id'].isin(shp_ids)]
    else:
        df_del = pd.DataFrame()

    del_ids = df_del['delivery_id'].tolist() if not df_del.empty and 'delivery_id' in df_del.columns else []
    
    raw_ins = datasets.get('inspections')
    if raw_ins is not None and not raw_ins.empty and 'delivery_id' in raw_ins.columns:
        df_ins = raw_ins[raw_ins['delivery_id'].isin(del_ids)]
    else:
        df_ins = pd.DataFrame()

    df_inv = _filter_df(datasets.get('invoices'), 'supplier_id', supplier_id)
    df_rsk = _filter_df(datasets.get('risk_signals'), 'supplier_id', supplier_id)
    contract_row = df_contracts.iloc[0] if not df_contracts.empty else None

    # Calculate individual dimensions
    del_res = calculate_delivery_score(df_del)
    qual_res = calculate_quality_score(df_ins)
    cost_res = calculate_cost_score(df_inv)
    cap_res = calculate_capacity_score(df_sites, df_pos)
    comp_res = calculate_compliance_score(contract_row, EVALUATION_DATE)
    risk_res = calculate_risk_score(df_rsk, EVALUATION_DATE)

    total_records = len(df_pos) + len(df_shp) + len(df_del) + len(df_ins) + len(df_inv)
    avg_confidence = round(
        (del_res['confidence'] + qual_res['confidence'] + cost_res['confidence'] +
         cap_res['confidence'] + comp_res['confidence'] + risk_res['confidence']) / 6.0,
        2
    )

    created_timestamp = f"{EVALUATION_DATE} 00:00:00"

    # Missing Evidence Guardrail
    if len(df_pos) < MIN_EVIDENCE_RECORDS:
        return {
            'score_id': f"SCORE-2026-{supplier_id}",
            'supplier_id': supplier_id,
            'evaluation_date': EVALUATION_DATE,
            'evaluation_window': EVALUATION_WINDOW,
            'delivery_score': del_res['delivery_score'],
            'quality_score': qual_res['quality_score'],
            'cost_score': cost_res['cost_score'],
            'capacity_score': cap_res['capacity_score'],
            'compliance_score': comp_res['compliance_score'],
            'risk_score': risk_res['risk_score'],
            'final_score': 0.0,
            'confidence_score': avg_confidence,
            'classification': 'Unrated',
            'recommended_action': 'Request additional performance information.',
            'methodology_version': METHODOLOGY_VERSION,
            'total_records_analyzed': total_records,
            'created_at': created_timestamp
        }

    final_score = (
        del_res['delivery_score'] * SCORING_WEIGHTS['delivery'] +
        qual_res['quality_score'] * SCORING_WEIGHTS['quality'] +
        cost_res['cost_score'] * SCORING_WEIGHTS['cost'] +
        cap_res['capacity_score'] * SCORING_WEIGHTS['capacity'] +
        comp_res['compliance_score'] * SCORING_WEIGHTS['compliance'] +
        risk_res['risk_score'] * SCORING_WEIGHTS['risk']
    )
    final_score = round(final_score, 2)

    if final_score >= 90.0:
        classification = 'Excellent'
        rec = 'Preferred supplier.'
    elif final_score >= 80.0:
        classification = 'Good'
        rec = 'Continue normal procurement.'
    elif final_score >= 70.0:
        classification = 'Moderate'
        rec = 'Monitor performance.'
    elif final_score >= 60.0:
        classification = 'Poor'
        rec = 'Create corrective action plan.'
    else:
        classification = 'Critical'
        rec = 'Escalate for procurement review.'

    return {
        'score_id': f"SCORE-2026-{supplier_id}",
        'supplier_id': supplier_id,
        'evaluation_date': EVALUATION_DATE,
        'evaluation_window': EVALUATION_WINDOW,
        'delivery_score': del_res['delivery_score'],
        'quality_score': qual_res['quality_score'],
        'cost_score': cost_res['cost_score'],
        'capacity_score': cap_res['capacity_score'],
        'compliance_score': comp_res['compliance_score'],
        'risk_score': risk_res['risk_score'],
        'final_score': final_score,
        'confidence_score': avg_confidence,
        'classification': classification,
        'recommended_action': rec,
        'methodology_version': METHODOLOGY_VERSION,
        'total_records_analyzed': total_records,
        'created_at': created_timestamp
    }