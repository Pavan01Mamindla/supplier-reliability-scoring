import pandas as pd
from datetime import datetime

def calculate_compliance_score(contract: pd.Series, evaluation_date: str = "2026-10-22") -> dict:
    if contract is None or contract.empty:
        return {
            'compliance_score': 40.0,
            'contract_status': 'None',
            'is_valid': False,
            'confidence': 0.5
        }

    c_end = datetime.strptime(contract['end_date'], '%Y-%m-%d')
    eval_dt = datetime.strptime(evaluation_date, '%Y-%m-%d')

    if contract['status'] != 'Active' or c_end < eval_dt:
        return {
            'compliance_score': 30.0,
            'contract_status': 'Expired/Invalid',
            'is_valid': False,
            'confidence': 1.0
        }

    return {
        'compliance_score': 100.0,
        'contract_status': 'Active',
        'is_valid': True,
        'confidence': 1.0
    }