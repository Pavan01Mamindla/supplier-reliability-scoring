import pytest
import pandas as pd
from src.scoring.delivery_score import calculate_delivery_score
from src.scoring.quality_score import calculate_quality_score
from src.scoring.cost_score import calculate_cost_score
from src.scoring.supplier_score import evaluate_supplier

def test_delivery_score_perfect():
    df_del = pd.DataFrame([
        {'delay_days': 0}, {'delay_days': -2}, {'delay_days': 0}, {'delay_days': 0}, {'delay_days': -1}
    ])
    res = calculate_delivery_score(df_del)
    assert res['delivery_score'] == 100.0
    assert res['ontime_rate'] == 100.0

def test_delivery_score_penalties():
    df_del = pd.DataFrame([
        {'delay_days': 10}, {'delay_days': 15}, {'delay_days': 20}
    ])
    res = calculate_delivery_score(df_del)
    assert res['delivery_score'] < 50.0
    assert res['ontime_rate'] == 0.0

def test_quality_score_defects():
    df_ins = pd.DataFrame([
        {'inspected_quantity': 100, 'rejected_quantity': 20, 'accepted_quantity': 80}
    ])
    res = calculate_quality_score(df_ins)
    assert res['defect_rate'] == 20.0
    assert res['quality_score'] == 50.0

def test_unrated_insufficient_evidence():
    datasets = {
        'suppliers': pd.DataFrame([{'supplier_id': 'SUP-000099', 'profile_type': 'Insufficient Data'}]),
        'sites': pd.DataFrame([]),
        'contracts': pd.DataFrame([]),
        'purchase_orders': pd.DataFrame([]),
        'shipments': pd.DataFrame([]),
        'delivery_events': pd.DataFrame([]),
        'inspections': pd.DataFrame([]),
        'invoices': pd.DataFrame([]),
        'risk_signals': pd.DataFrame([])
    }
    score = evaluate_supplier('SUP-000099', datasets)
    assert score['classification'] == 'Unrated'
    assert score['final_score'] == 0.0