import numpy as np
import pandas as pd

def calculate_delivery_score(deliveries: pd.DataFrame) -> dict:
    if deliveries.empty:
        return {
            'delivery_score': 50.0,
            'ontime_rate': 0.0,
            'avg_delay_days': 0.0,
            'total_deliveries': 0,
            'confidence': 0.0
        }

    total = len(deliveries)
    ontime_count = (deliveries['delay_days'] <= 0).sum()
    ontime_rate = (ontime_count / total) * 100.0

    avg_delay = float(deliveries['delay_days'].mean())
    delay_penalty = max(0.0, avg_delay * 3.5)
    raw_score = max(0.0, min(100.0, ontime_rate - delay_penalty))

    return {
        'delivery_score': round(float(raw_score), 2),
        'ontime_rate': round(float(ontime_rate), 2),
        'avg_delay_days': round(avg_delay, 2),
        'total_deliveries': total,
        'confidence': 1.0 if total >= 5 else round(total / 5.0, 2)
    }