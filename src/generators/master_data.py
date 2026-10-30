import numpy as np
import pandas as pd
from datetime import datetime
from src.config import RANDOM_SEED

CATEGORIES = ['Raw Materials', 'Electronics', 'Packaging', 'Mechanical Components', 'Logistics Services']
COUNTRIES = ['USA', 'Germany', 'Japan', 'South Korea', 'Taiwan', 'India', 'Mexico', 'Vietnam']
CITIES = {
    'USA': ['Austin', 'Chicago', 'San Jose'],
    'Germany': ['Stuttgart', 'Munich', 'Hamburg'],
    'Japan': ['Osaka', 'Nagoya', 'Tokyo'],
    'South Korea': ['Incheon', 'Suwon', 'Busan'],
    'Taiwan': ['Hsinchu', 'Taichung', 'Tainan'],
    'India': ['Bengaluru', 'Pune', 'Chennai'],
    'Mexico': ['Monterrey', 'Guadalajara', 'Tijuana'],
    'Vietnam': ['Hai Phong', 'Da Nang', 'Binh Duong']
}

PROFILES = [
    'Highly Reliable', 'Average', 'Poor Performing', 'Deteriorating Delivery',
    'Recurring Quality Issues', 'Invoice Discrepancies', 'Limited Capacity',
    'Compliance Violations', 'Disruption Affected', 'Insufficient Data'
]

def generate_suppliers_and_sites(n_suppliers: int = 100, seed: int = RANDOM_SEED):
    rng = np.random.default_rng(seed)
    suppliers = []
    sites = []
    contracts = []

    profile_assignments = rng.choice(PROFILES, size=n_suppliers, p=[0.20, 0.25, 0.10, 0.10, 0.08, 0.07, 0.05, 0.05, 0.05, 0.05])

    for i in range(1, n_suppliers + 1):
        sup_id = f"SUP-{i:06d}"
        profile = profile_assignments[i - 1]
        cat = rng.choice(CATEGORIES)
        country = rng.choice(COUNTRIES)
        
        status = 'Active'
        risk = 'Low'
        if profile in ['Poor Performing', 'Compliance Violations']:
            risk = 'High'
            status = 'Probation' if profile == 'Poor Performing' else 'Suspended'
        elif profile in ['Deteriorating Delivery', 'Disruption Affected', 'Recurring Quality Issues']:
            risk = 'Medium'

        suppliers.append({
            'supplier_id': sup_id,
            'name': f"Supplier Global {i} Corp",
            'category': cat,
            'country': country,
            'status': status,
            'risk_level': risk,
            'profile_type': profile,
            'created_at': '2025-01-01 00:00:00'
        })

        num_sites = 1 if profile == 'Limited Capacity' else int(rng.integers(1, 4))
        for s in range(1, num_sites + 1):
            site_id = f"SITE-{sup_id}-{s:02d}"
            city = rng.choice(CITIES[country])
            base_capacity = 500 if profile == 'Limited Capacity' else int(rng.integers(2000, 10000))
            sites.append({
                'site_id': site_id,
                'supplier_id': sup_id,
                'site_name': f"{city} Manufacturing Facility {s}",
                'city': city,
                'country': country,
                'capacity_units_per_month': base_capacity,
                'is_active': 1,
                'created_at': '2025-01-01 00:00:00'
            })

        c_status = 'Expired' if profile == 'Compliance Violations' else 'Active'
        contracts.append({
            'contract_id': f"CTR-{sup_id}-01",
            'supplier_id': sup_id,
            'start_date': '2025-01-01',
            'end_date': '2025-12-31' if profile == 'Compliance Violations' else '2027-12-31',
            'committed_volume': int(rng.integers(5000, 50000)),
            'agreed_unit_price': float(np.round(rng.uniform(10.0, 500.0), 2)),
            'status': c_status,
            'created_at': '2025-01-01 00:00:00'
        })

    return pd.DataFrame(suppliers), pd.DataFrame(sites), pd.DataFrame(contracts)