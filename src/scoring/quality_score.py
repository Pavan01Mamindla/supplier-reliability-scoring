import pandas as pd

def calculate_quality_score(inspections: pd.DataFrame) -> dict:
    if inspections.empty:
        return {
            'quality_score': 50.0,
            'pass_rate': 0.0,
            'defect_rate': 0.0,
            'total_inspections': 0,
            'confidence': 0.0
        }

    total_inspected = inspections['inspected_quantity'].sum()
    total_rejected = inspections['rejected_quantity'].sum()
    total_accepted = inspections['accepted_quantity'].sum()

    if total_inspected == 0:
        defect_rate = 0.0
        pass_rate = 100.0
    else:
        defect_rate = (total_rejected / total_inspected) * 100.0
        pass_rate = (total_accepted / total_inspected) * 100.0

    raw_score = max(0.0, min(100.0, 100.0 - (defect_rate * 2.5)))

    return {
        'quality_score': round(float(raw_score), 2),
        'pass_rate': round(float(pass_rate), 2),
        'defect_rate': round(float(defect_rate), 2),
        'total_inspections': len(inspections),
        'confidence': 1.0 if len(inspections) >= 5 else round(len(inspections) / 5.0, 2)
    }