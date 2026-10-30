import pandas as pd

def calculate_capacity_score(sites: pd.DataFrame, pos: pd.DataFrame) -> dict:
    if sites.empty:
        return {
            'capacity_score': 50.0,
            'total_capacity': 0,
            'capacity_utilization': 0.0,
            'confidence': 0.0
        }

    total_capacity = sites['capacity_units_per_month'].sum()
    monthly_ordered = pos['total_amount'].count() * 150

    utilization = (monthly_ordered / max(total_capacity, 1)) * 100.0

    if utilization < 80.0:
        score = 100.0
    elif utilization <= 100.0:
        score = 80.0
    else:
        score = max(20.0, 100.0 - (utilization - 100.0) * 1.5)

    return {
        'capacity_score': round(float(score), 2),
        'total_capacity': int(total_capacity),
        'capacity_utilization': round(float(utilization), 2),
        'confidence': 0.85
    }