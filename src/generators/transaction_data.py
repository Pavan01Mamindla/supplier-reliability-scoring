import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.config import RANDOM_SEED

def generate_purchase_orders_and_lines(df_suppliers, df_sites, df_contracts, n_pos: int = 1000, seed: int = RANDOM_SEED):
    rng = np.random.default_rng(seed)
    pos = []
    po_lines = []

    active_suppliers = df_suppliers[df_suppliers['profile_type'] != 'Insufficient Data']
    insufficient_suppliers = df_suppliers[df_suppliers['profile_type'] == 'Insufficient Data']
    
    all_sup_ids = active_suppliers['supplier_id'].values
    sparse_sup_ids = insufficient_suppliers['supplier_id'].values

    site_map = df_sites.groupby('supplier_id')['site_id'].apply(list).to_dict()
    contract_map = df_contracts.set_index('supplier_id')['contract_id'].to_dict()
    price_map = df_contracts.set_index('contract_id')['agreed_unit_price'].to_dict()

    base_date = datetime(2025, 1, 15)

    for i in range(1, n_pos + 1):
        po_id = f"PO-2026-{i:06d}"
        if i <= len(sparse_sup_ids):
            sup_id = sparse_sup_ids[i - 1]
        else:
            sup_id = rng.choice(all_sup_ids)

        assigned_site = rng.choice(site_map[sup_id])
        assigned_contract = contract_map[sup_id]
        agreed_price = price_map[assigned_contract]

        offset_days = int(rng.integers(0, 600))
        order_dt = base_date + timedelta(days=offset_days)
        lead_time = int(rng.integers(14, 45))
        promised_dt = order_dt + timedelta(days=lead_time)

        num_lines = int(rng.integers(1, 4))
        po_total = 0.0

        for l in range(1, num_lines + 1):
            line_id = f"POL-{po_id}-{l:02d}"
            qty = int(rng.integers(10, 500))
            line_total = round(qty * agreed_price, 2)
            po_total += line_total

            po_lines.append({
                'po_line_id': line_id,
                'po_id': po_id,
                'line_number': l,
                'item_sku': f"SKU-{int(rng.integers(1000, 9999))}",
                'ordered_quantity': qty,
                'unit_price': agreed_price,
                'line_total': line_total,
                'created_at': order_dt.strftime('%Y-%m-%d %H:%M:%S')
            })

        pos.append({
            'po_id': po_id,
            'supplier_id': sup_id,
            'site_id': assigned_site,
            'contract_id': assigned_contract,
            'order_date': order_dt.strftime('%Y-%m-%d'),
            'promised_delivery_date': promised_dt.strftime('%Y-%m-%d'),
            'total_amount': round(po_total, 2),
            'status': 'Fulfilled',
            'created_at': order_dt.strftime('%Y-%m-%d %H:%M:%S')
        })

    return pd.DataFrame(pos), pd.DataFrame(po_lines)