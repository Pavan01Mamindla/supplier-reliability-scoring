PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS supplier_scores;
DROP TABLE IF EXISTS risk_signals;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS inspections;
DROP TABLE IF EXISTS delivery_events;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS po_lines;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS contracts;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS suppliers;

CREATE TABLE suppliers (
    supplier_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('Raw Materials', 'Electronics', 'Packaging', 'Mechanical Components', 'Logistics Services')),
    country TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Active', 'Probation', 'Suspended', 'Inactive')),
    risk_level TEXT NOT NULL CHECK(risk_level IN ('Low', 'Medium', 'High', 'Critical')),
    profile_type TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE sites (
    site_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    site_name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    capacity_units_per_month INTEGER NOT NULL CHECK(capacity_units_per_month > 0),
    is_active INTEGER NOT NULL CHECK(is_active IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
);

CREATE TABLE contracts (
    contract_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    committed_volume INTEGER NOT NULL CHECK(committed_volume >= 0),
    agreed_unit_price REAL NOT NULL CHECK(agreed_unit_price >= 0),
    status TEXT NOT NULL CHECK(status IN ('Active', 'Expired', 'Terminated')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE CASCADE
);

CREATE TABLE purchase_orders (
    po_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    site_id TEXT NOT NULL,
    contract_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    promised_delivery_date TEXT NOT NULL,
    total_amount REAL NOT NULL CHECK(total_amount >= 0),
    status TEXT NOT NULL CHECK(status IN ('Draft', 'Confirmed', 'In Transit', 'Fulfilled', 'Cancelled')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (site_id) REFERENCES sites(site_id),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id)
);

CREATE TABLE po_lines (
    po_line_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    item_sku TEXT NOT NULL,
    ordered_quantity INTEGER NOT NULL CHECK(ordered_quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    line_total REAL NOT NULL CHECK(line_total >= 0),
    created_at TEXT NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE
);

CREATE TABLE shipments (
    shipment_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    site_id TEXT NOT NULL,
    dispatch_date TEXT NOT NULL,
    shipped_quantity INTEGER NOT NULL CHECK(shipped_quantity >= 0),
    carrier TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Dispatched', 'Delivered', 'Delayed', 'Lost')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

CREATE TABLE delivery_events (
    delivery_id TEXT PRIMARY KEY,
    shipment_id TEXT NOT NULL,
    actual_delivery_date TEXT NOT NULL,
    received_quantity INTEGER NOT NULL CHECK(received_quantity >= 0),
    delivery_status TEXT NOT NULL CHECK(delivery_status IN ('On-Time', 'Delayed', 'Early', 'Failed')),
    delay_days INTEGER NOT NULL,
    warehouse_code TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);

CREATE TABLE inspections (
    inspection_id TEXT PRIMARY KEY,
    delivery_id TEXT NOT NULL,
    inspected_quantity INTEGER NOT NULL CHECK(inspected_quantity >= 0),
    accepted_quantity INTEGER NOT NULL CHECK(accepted_quantity >= 0),
    rejected_quantity INTEGER NOT NULL CHECK(rejected_quantity >= 0),
    defect_type TEXT NOT NULL CHECK(defect_type IN ('None', 'Dimensional', 'Contamination', 'Functional', 'Packaging', 'Labeling')),
    inspection_result TEXT NOT NULL CHECK(inspection_result IN ('Passed', 'Conditional Pass', 'Failed')),
    inspection_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (delivery_id) REFERENCES delivery_events(delivery_id)
);

CREATE TABLE invoices (
    invoice_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    invoice_date TEXT NOT NULL,
    invoice_amount REAL NOT NULL CHECK(invoice_amount >= 0),
    expected_amount REAL NOT NULL CHECK(expected_amount >= 0),
    amount_variance REAL NOT NULL,
    variance_percentage REAL NOT NULL,
    payment_status TEXT NOT NULL CHECK(payment_status IN ('Pending', 'Approved', 'Disputed', 'Paid')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE risk_signals (
    signal_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    event_date TEXT NOT NULL,
    source TEXT,
    severity REAL NOT NULL CHECK(severity >= 0.0 AND severity <= 10.0),
    description TEXT NOT NULL,
    recovery_status TEXT NOT NULL CHECK(recovery_status IN ('Active', 'Monitoring', 'Resolved')),
    created_at TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE supplier_scores (
    score_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    evaluation_date TEXT NOT NULL,
    evaluation_window TEXT NOT NULL,
    delivery_score REAL NOT NULL,
    quality_score REAL NOT NULL,
    cost_score REAL NOT NULL,
    capacity_score REAL NOT NULL,
    compliance_score REAL NOT NULL,
    risk_score REAL NOT NULL,
    final_score REAL NOT NULL,
    confidence_score REAL NOT NULL,
    classification TEXT NOT NULL CHECK(classification IN ('Excellent', 'Good', 'Moderate', 'Poor', 'Critical', 'Unrated')),
    recommended_action TEXT NOT NULL,
    methodology_version TEXT NOT NULL,
    total_records_analyzed INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_shipment_po ON shipments(po_id);
CREATE INDEX idx_delivery_shipment ON delivery_events(shipment_id);
CREATE INDEX idx_inspection_delivery ON inspections(delivery_id);
CREATE INDEX idx_invoice_po ON invoices(po_id);
CREATE INDEX idx_risk_supplier ON risk_signals(supplier_id);
CREATE INDEX idx_score_supplier ON supplier_scores(supplier_id);