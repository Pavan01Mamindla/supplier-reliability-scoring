import pandas as pd
from datetime import datetime

def calculate_risk_score(risk_signals: pd.DataFrame, evaluation_date: str = "2026-10-22") -> dict:
    if risk_signals.empty:
        return {
            'risk_score': 100.0,
            'max_severity': 0.0,
            'signal_count': 0,
            'confidence': 0.7
        }

    eval_dt = datetime.strptime(evaluation_date, '%Y-%m-%d')
    valid_signals = []
    
    for _, row in risk_signals.iterrows():
        if row.get('event_date'):
            try:
                sig_dt = datetime.strptime(row['event_date'], '%Y-%m-%d')
                if sig_dt <= eval_dt:
                    valid_signals.append(row)
            except Exception:
                continue

    if not valid_signals:
        return {
            'risk_score': 100.0,
            'max_severity': 0.0,
            'signal_count': 0,
            'confidence': 0.7
        }

    df_valid = pd.DataFrame(valid_signals)
    max_sev = float(df_valid['severity'].max())
    active_count = (df_valid['recovery_status'] == 'Active').sum()

    penalty = (max_sev * 7.0) + (active_count * 8.0)
    raw_score = max(0.0, min(100.0, 100.0 - penalty))

    return {
        'risk_score': round(float(raw_score), 2),
        'max_severity': round(max_sev, 2),
        'signal_count': len(df_valid),
        'confidence': 1.0
    }