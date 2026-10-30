import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Supplier Reliability Intelligence", layout="wide", page_icon="📊")

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "supplier_system.db"

@st.cache_data
def load_table(table_name: str):
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df

st.sidebar.title("Procurement AI")
page = st.sidebar.radio("Navigation", [
    "1. Executive Overview",
    "2. Supplier Ranking & Performance",
    "3. Explainable Scorecard",
    "4. Risk Signals & Anomalies",
    "5. Delivery & Quality Analytics",
    "6. Cost & Contract Compliance",
    "7. Data Validation & Integrity"
])

suppliers = load_table("suppliers")
scores = load_table("supplier_scores")
pos = load_table("purchase_orders")
deliveries = load_table("delivery_events")
inspections = load_table("inspections")
invoices = load_table("invoices")
risks = load_table("risk_signals")

if scores.empty:
    st.error("Pipeline database not detected. Please run `python scripts/run_pipeline.py` first.")
    st.stop()

# PAGE 1: EXECUTIVE OVERVIEW
if page == "1. Executive Overview":
    st.title("Executive Procurement Intelligence Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Active Suppliers", len(suppliers))
    with col2:
        st.metric("Average Reliability Score", f"{scores['final_score'].mean():.1f} / 100")
    with col3:
        high_risk_count = len(scores[scores['classification'].isin(['Poor', 'Critical'])])
        st.metric("Critical / Poor Suppliers", high_risk_count)
    with col4:
        unrated = len(scores[scores['classification'] == 'Unrated'])
        st.metric("Unrated Suppliers", unrated)

    st.markdown("---")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Supplier Classification Distribution")
        fig_pie = px.pie(scores, names='classification', color='classification',
                         color_discrete_map={
                             'Excellent': '#2ecc71',
                             'Good': '#3498db',
                             'Moderate': '#f1c40f',
                             'Poor': '#e67e22',
                             'Critical': '#e74c3c',
                             'Unrated': '#95a5a6'
                         })
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Component Dimension Averages")
        dim_means = {
            'Delivery': scores['delivery_score'].mean(),
            'Quality': scores['quality_score'].mean(),
            'Cost': scores['cost_score'].mean(),
            'Capacity': scores['capacity_score'].mean(),
            'Compliance': scores['compliance_score'].mean(),
            'Risk Mitigation': scores['risk_score'].mean()
        }
        fig_bar = px.bar(x=list(dim_means.keys()), y=list(dim_means.values()),
                         labels={'x': 'Dimension', 'y': 'Average Score'},
                         color=list(dim_means.values()), color_continuous_scale="Viridis")
        st.plotly_chart(fig_bar, use_container_width=True)

# PAGE 2: SUPPLIER RANKING
elif page == "2. Supplier Ranking & Performance":
    st.title("Supplier Rankings & Directory")
    merged = scores.merge(suppliers, on='supplier_id')
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_class = st.multiselect("Filter Classification", merged['classification'].unique(), default=merged['classification'].unique())
    with col_f2:
        selected_cat = st.multiselect("Filter Category", merged['category'].unique(), default=merged['category'].unique())

    filtered = merged[(merged['classification'].isin(selected_class)) & (merged['category'].isin(selected_cat))]
    st.dataframe(filtered[['supplier_id', 'name', 'category', 'country', 'final_score', 'classification', 'confidence_score', 'recommended_action']], use_container_width=True)

# PAGE 3: EXPLAINABLE SCORECARD
elif page == "3. Explainable Scorecard":
    st.title("Explainable Individual Scorecard")
    sup_list = suppliers['supplier_id'].tolist()
    selected_sup = st.selectbox("Select Supplier ID", sup_list)

    sup_score = scores[scores['supplier_id'] == selected_sup].iloc[0]
    sup_info = suppliers[suppliers['supplier_id'] == selected_sup].iloc[0]

    st.subheader(f"Evaluation for {sup_info['name']} ({selected_sup})")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Final Weighted Score", f"{sup_score['final_score']} / 100")
    sc2.metric("Classification", sup_score['classification'])
    sc3.metric("Data Confidence", f"{sup_score['confidence_score'] * 100:.0f}%")

    st.markdown("#### Performance Radar")
    categories = ['Delivery', 'Quality', 'Cost', 'Capacity', 'Compliance', 'Risk']
    values = [
        sup_score['delivery_score'], sup_score['quality_score'], sup_score['cost_score'],
        sup_score['capacity_score'], sup_score['compliance_score'], sup_score['risk_score']
    ]
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Supplier Score'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.plotly_chart(fig_radar, use_container_width=True)

    st.info(f"**Action Recommendation:** {sup_score['recommended_action']}")

# PAGE 4: RISK SIGNALS & ANOMALIES
elif page == "4. Risk Signals & Anomalies":
    st.title("Disruption Risk Signals & Ground Truth Validation")
    st.subheader("Active Risk Signals")
    st.dataframe(risks[['signal_id', 'supplier_id', 'event_date', 'source', 'severity', 'recovery_status', 'description']], use_container_width=True)

# PAGE 5: DELIVERY & QUALITY ANALYTICS
elif page == "5. Delivery & Quality Analytics":
    st.title("Delivery & Inspection Quality Analytics")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Delay Distribution (Days)")
        fig_del = px.histogram(deliveries, x="delay_days", nbins=30, color="delivery_status")
        st.plotly_chart(fig_del, use_container_width=True)
    with c2:
        st.subheader("Inspection Result Breakdown")
        fig_ins = px.pie(inspections, names="inspection_result", color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_ins, use_container_width=True)

# PAGE 6: COST & CONTRACT COMPLIANCE
elif page == "6. Cost & Contract Compliance":
    st.title("Cost Discrepancies & Billing Variance")
    st.subheader("Invoice Variance vs Expected Amounts")
    fig_scatter = px.scatter(invoices, x="expected_amount", y="invoice_amount", color="payment_status", size="variance_percentage")
    st.plotly_chart(fig_scatter, use_container_width=True)

# PAGE 7: DATA VALIDATION & INTEGRITY
elif page == "7. Data Validation & Integrity":
    st.title("System Health & Automated Validation Checks")
    rep_path = Path(__file__).resolve().parent.parent / "outputs" / "reports" / "validation_report.csv"
    if rep_path.exists():
        vdf = pd.read_csv(rep_path)
        st.dataframe(vdf, use_container_width=True)
    else:
        st.warning("Validation report not found on disk.")