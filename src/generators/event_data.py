import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.config import RANDOM_SEED

CARRIERS = ['Maersk', 'DHL Supply Chain', 'Kuehne+Nagel', 'FedEx Logistics', 'DB Schenker']
WAREHOUSES = ['WH-CENTRAL-01', 'WH-EAST-02', 'WH-WEST-03', 'WH-EUROPE-01', 'WH-ASIA-01']

def generate_events(df_pos, df_suppliers, n_shipments: int = 1500, n_inspections: int = 2000, seed: int = RANDOM_SEED):
    rng = np.random.default_rng(seed)
    shipments = []
    delivery_events = []
    inspections = []
    invoices = []
    risk_signals = []

    profile_map = df_suppliers.set_index('supplier_id')['profile_type'].to_dict()
    po_records = df_pos.to_dict(orient='records')
    po_count = len(po_records)

    for i in range(1, n_shipments + 1):
        shp_id = f"SHP-2026-{i:06d}"
        po = po_records[(i - 1) % po_count]
        sup_id = po['supplier_id']
        profile = profile_map.get(sup_id, 'Average')

        po_order_dt = datetime.strptime(po['order_date'], '%Y-%m-%d')
        promised_dt = datetime.strptime(po['promised_delivery_date'], '%Y-%m-%d')

        dispatch_offset = int(rng.integers(5, 20))
        dispatch_dt = po_order_dt + timedelta(days=dispatch_offset)

        transit_days = int(rng.integers(5, 15))
        if profile in ['Poor Performing', 'Deteriorating Delivery']:
            transit_days += int(rng.integers(10, 30))

        actual_delivery_dt = dispatch_dt + timedelta(days=transit_days)
        delay_days = (actual_delivery_dt - promised_dt).days

        status = 'On-Time'
        if delay_days > 0:
            status = 'Delayed'
        elif delay_days < -3:
            status = 'Early'

        shipments.append({
            'shipment_id': shp_id,
            'po_id': po['po_id'],
            'supplier_id': sup_id,
            'site_id': po['site_id'],
            'dispatch_date': dispatch_dt.strftime('%Y-%m-%d'),
            'shipped_quantity': 100,
            'carrier': rng.choice(CARRIERS),
            'status': 'Delivered',
            'created_at': dispatch_dt.strftime('%Y-%m-%d %H:%M:%S')
        })

        del_id = f"DEL-2026-{i:06d}"
        delivery_events.append({
            'delivery_id': del_id,
            'shipment_id': shp_id,
            'actual_delivery_date': actual_delivery_dt.strftime('%Y-%m-%d'),
            'received_quantity': 100,
            'delivery_status': status,
            'delay_days': int(delay_days),
            'warehouse_code': rng.choice(WAREHOUSES),
            'created_at': actual_delivery_dt.strftime('%Y-%m-%d %H:%M:%S')
        })

        inv_id = f"INV-2026-{i:06d}"
        expected_amt = po['total_amount']
        var_pct = 0.0
        if profile == 'Invoice Discrepancies':
            var_pct = float(rng.uniform(0.10, 0.35))
        elif profile == 'Poor Performing':
            var_pct = float(rng.uniform(0.05, 0.15))

        inv_amt = round(expected_amt * (1.0 + var_pct), 2)
        variance = round(inv_amt - expected_amt, 2)

        invoices.append({
            'invoice_id': inv_id,
            'po_id': po['po_id'],
            'supplier_id': sup_id,
            'invoice_date': actual_delivery_dt.strftime('%Y-%m-%d'),
            'invoice_amount': inv_amt,
            'expected_amount': expected_amt,
            'amount_variance': variance,
            'variance_percentage': round(var_pct * 100, 2),
            'payment_status': 'Disputed' if var_pct > 0.05 else 'Paid',
            'created_at': actual_delivery_dt.strftime('%Y-%m-%d %H:%M:%S')
        })

    del_records = delivery_events
    del_count = len(del_records)

    for k in range(1, n_inspections + 1):
        insp_id = f"INS-2026-{k:06d}"
        del_ev = del_records[(k - 1) % del_count]
        del_date = datetime.strptime(del_ev['actual_delivery_date'], '%Y-%m-%d')
        insp_date = del_date + timedelta(days=1)

        shp_idx = (k - 1) % del_count
        sup_id = shipments[shp_idx]['supplier_id']
        profile = profile_map.get(sup_id, 'Average')

        inspected_qty = 100
        rejected_qty = 0
        defect = 'None'
        res = 'Passed'

        if profile in ['Recurring Quality Issues', 'Poor Performing']:
            rej_rate = rng.uniform(0.15, 0.40)
            rejected_qty = int(inspected_qty * rej_rate)
            defect = rng.choice(['Dimensional', 'Functional', 'Contamination'])
            res = 'Failed'
        elif profile == 'Average':
            if rng.random() < 0.10:
                rejected_qty = int(rng.integers(1, 10))
                defect = 'Packaging'
                res = 'Conditional Pass'

        accepted_qty = inspected_qty - rejected_qty

        inspections.append({
            'inspection_id': insp_id,
            'delivery_id': del_ev['delivery_id'],
            'inspected_quantity': inspected_qty,
            'accepted_quantity': accepted_qty,
            'rejected_quantity': rejected_qty,
            'defect_type': defect,
            'inspection_result': res,
            'inspection_date': insp_date.strftime('%Y-%m-%d'),
            'created_at': insp_date.strftime('%Y-%m-%d %H:%M:%S')
        })

    sig_counter = 1
    for s in df_suppliers.to_dict(orient='records'):
        sup_id = s['supplier_id']
        profile = s['profile_type']
        
        if profile in ['Disruption Affected', 'Poor Performing', 'Compliance Violations']:
            num_sig = int(rng.integers(2, 5))
            for _ in range(num_sig):
                sig_id = f"RSK-{sup_id}-2026-{sig_counter:02d}"
                sig_counter += 1
                ev_dt = datetime(2026, int(rng.integers(1, 9)), int(rng.integers(1, 28)))
                severity = round(float(rng.uniform(6.0, 9.5)), 1) if profile != 'Average' else 3.0
                risk_signals.append({
                    'signal_id': sig_id,
                    'supplier_id': sup_id,
                    'event_date': ev_dt.strftime('%Y-%m-%d'),
                    'source': 'SupplyChainMonitor API',
                    'severity': severity,
                    'description': 'Port congestion and manufacturing downtime' if profile == 'Disruption Affected' else 'Regulatory compliance citation',
                    'recovery_status': 'Active' if severity > 7.0 else 'Resolved',
                    'created_at': ev_dt.strftime('%Y-%m-%d %H:%M:%S')
                })

    return (
        pd.DataFrame(shipments),
        pd.DataFrame(delivery_events),
        pd.DataFrame(inspections),
        pd.DataFrame(invoices),
        pd.DataFrame(risk_signals)
    )