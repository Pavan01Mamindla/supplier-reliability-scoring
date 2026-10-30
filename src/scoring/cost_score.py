import pandas as pd

def calculate_cost_score(invoices: pd.DataFrame) -> dict:
    if invoices.empty:
        return {
            'cost_score': 50.0,
            'avg_variance_pct': 0.0,
            'disputed_count': 0,
            'total_invoices': 0,
            'confidence': 0.0
        }

    avg_variance = float(invoices['variance_percentage'].mean())
    disputed = (invoices['payment_status'] == 'Disputed').sum()

    penalty = (avg_variance * 2.0) + (disputed * 5.0)
    raw_score = max(0.0, min(100.0, 100.0 - penalty))

    return {
        'cost_score': round(float(raw_score), 2),
        'avg_variance_pct': round(avg_variance, 2),
        'disputed_count': int(disputed),
        'total_invoices': len(invoices),
        'confidence': 1.0 if len(invoices) >= 3 else round(len(invoices) / 3.0, 2)
    }