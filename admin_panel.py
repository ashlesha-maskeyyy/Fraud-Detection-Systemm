import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="BuddhaAI Admin Console", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-title { color: #1e293b; font-size: 36px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("🛂 BuddhaAI Admin")
st.sidebar.write("Real-time Network Monitor")
st.sidebar.info("Connection: abc.db (Local)\nStatus: Operational")

if st.sidebar.button("🔄 REFRESH FEED"):
    st.rerun()

def get_admin_data():
    try:
        conn = sqlite3.connect('abc.db')
        query = "SELECT * FROM txn_logs ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()

st.markdown('<p class="main-title">Fraud Monitoring Command Center</p>', unsafe_allow_html=True)
st.write(f"System status checked at: {datetime.now().strftime('%H:%M:%S')}")

df = get_admin_data()

if not df.empty:
    kpi1, kpi2, kpi3 = st.columns(3)
    
    total_count = len(df)
    fraud_count = len(df[df['prediction'] == 'FRAUD'])
    
    kpi1.metric("Total Transactions", total_count)
    kpi2.metric("Fraud Blocks", fraud_count, delta=f"{fraud_count} blocked", delta_color="inverse")
    kpi3.metric("Network Health", "100%", delta="Optimal")

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Safety Distribution")
        fig_pie = px.pie(df, names='prediction', hole=0.4,
                         color='prediction',
                         color_discrete_map={'LEGITIMATE':'#2ecc71', 'FRAUD':'#e74c3c'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.subheader("Risk Level Frequency")
        risk_order = {"risk_level": ["Low", "Medium", "High"]}
        fig_bar = px.histogram(df, x="risk_level", color="risk_level",
                               color_discrete_map={'Low':'#2ecc71', 'Medium':'#f1c40f', 'High':'#e74c3c'},
                               category_orders=risk_order)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    st.subheader("📜 Live Transaction Audit Log")
    st.write("Below are the detailed records of every AI intervention.")
    
    st.dataframe(
        df[['timestamp', 'type', 'amount', 'fraud_probability', 'prediction', 'risk_level']],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No transactions detected yet. Please use the eSewa Client App to generate data.")