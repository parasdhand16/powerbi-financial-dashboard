import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Corporate Finance Suite", page_icon="🏦", layout="wide")

# =======================================================
# 1. GENERATE SYNTHETIC MULTI-NATIONAL FINANCIAL DATABASE
# =======================================================
@st.cache_data
def generate_financials():
    np.random.seed(42)
    dates = pd.date_range(start="2021-01-01", end="2023-12-31", freq='M')
    departments = ['Engineering', 'Marketing', 'Sales', 'Operations', 'Executive']
    regions = ['North America', 'EMEA', 'APAC']
    
    records = []
    base_revenue = 5000000
    
    for dt in dates:
        # Simulate macroeconomic growth
        growth_factor = 1 + (dt.year - 2021) * 0.15 + (dt.month * 0.01)
        
        for reg in regions:
            # Regional variances
            reg_mult = 1.2 if reg == 'North America' else (0.9 if reg == 'EMEA' else 1.5)
            monthly_rev = base_revenue * growth_factor * reg_mult * np.random.normal(1, 0.05)
            cogs = monthly_rev * np.random.uniform(0.35, 0.45) # 35-45% COGS
            
            for dept in departments:
                # Opex allocation
                opex = monthly_rev * np.random.uniform(0.05, 0.12)
                capex = np.random.choice([0, 0, opex * 2]) # Lumpy capex investments
                
                records.append({
                    'Date': dt,
                    'Region': reg,
                    'Department': dept,
                    'Revenue': monthly_rev / len(departments), # Allocated for simplicity
                    'COGS': cogs / len(departments),
                    'OPEX': opex,
                    'CAPEX': capex
                })
                
    df = pd.DataFrame(records)
    df['Gross_Profit'] = df['Revenue'] - df['COGS']
    df['EBITDA'] = df['Gross_Profit'] - df['OPEX']
    df['Free_Cash_Flow'] = df['EBITDA'] - df['CAPEX']
    return df

df = generate_financials()

st.title("🏦 Corporate FP&A Intelligence Dashboard")
st.markdown("Dynamic Executive Financial Controller suite featuring live Income Statement tracking, Cash Flow liquidity analytics, and interactive Scenario Planning.")

# =======================================================
# 2. STORYLINE TABS
# =======================================================
tab1, tab2, tab3 = st.tabs(["📊 Executive Income Statement", "💸 Cash & Liquidity Dynamics", "🔮 FP&A Scenario Modeling"])

# --- TAB 1: INCOME STATEMENT (WATERFALL) ---
with tab1:
    st.header("Global P&L Tracking")
    
    col1, col2 = st.columns(2)
    min_date, max_date = st.select_slider("Select Reporting Period", options=df['Date'].dt.date.unique(), value=(df['Date'].dt.date.min(), df['Date'].dt.date.max()))
    mask = (df['Date'].dt.date >= min_date) & (df['Date'].dt.date <= max_date)
    filtered = df.loc[mask]
    
    # Financial Aggregations
    tot_rev = filtered['Revenue'].sum()
    tot_cogs = filtered['COGS'].sum() * -1
    tot_gp = filtered['Gross_Profit'].sum()
    tot_opex = filtered['OPEX'].sum() * -1
    tot_ebitda = filtered['EBITDA'].sum()
    
    st.subheader("Financial Waterfall (Revenue to EBITDA)")
    fig_waterfall = go.Figure(go.Waterfall(
        name="P&L", orientation="v",
        measure=["relative", "relative", "total", "relative", "total"],
        x=["Topline Revenue", "COGS", "Gross Profit", "Operating Expenses", "EBITDA"],
        textposition="outside",
        text=[f"${tot_rev/1e6:.1f}M", f"${tot_cogs/1e6:.1f}M", f"${tot_gp/1e6:.1f}M", f"${tot_opex/1e6:.1f}M", f"${tot_ebitda/1e6:.1f}M"],
        y=[tot_rev, tot_cogs, 0, tot_opex, 0],
        connector={"line":{"color":"rgb(63, 63, 63)"}},
        decreasing={"marker":{"color":"#d62728"}},
        increasing={"marker":{"color":"#2ca02c"}},
        totals={"marker":{"color":"#1f77b4"}}
    ))
    fig_waterfall.update_layout(title="Corporate Income Statement Progression", showlegend=False)
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Departmental Opex Breakdown
    st.subheader("Operating Expenditure (OPEX) by Cost Center")
    fig_pie = px.pie(filtered, values='OPEX', names='Department', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: CASH FLOW ---
with tab2:
    st.header("Liquidity & Cash Burn Analytics")
    st.markdown("Tracking trailing Free Cash Flow (FCF) after Capital Expenditures (CAPEX).")
    
    time_grouped = filtered.groupby('Date')[['EBITDA', 'CAPEX', 'Free_Cash_Flow']].sum().reset_index()
    
    fig_cash = go.Figure()
    fig_cash.add_trace(go.Bar(x=time_grouped['Date'], y=time_grouped['EBITDA'], name='EBITDA (Cash Generated)', marker_color='#2ca02c'))
    fig_cash.add_trace(go.Bar(x=time_grouped['Date'], y=time_grouped['CAPEX'] * -1, name='CAPEX (Cash Burn/Inv)', marker_color='#d62728'))
    fig_cash.add_trace(go.Scatter(x=time_grouped['Date'], y=time_grouped['Free_Cash_Flow'], name='Net Free Cash Flow', mode='lines+markers', line=dict(color='black', width=3)))
    
    fig_cash.update_layout(barmode='relative', title="Monthly Cash Flow Reconciliation", xaxis_title="Reporting Month", yaxis_title="Dollars ($ USD)")
    st.plotly_chart(fig_cash, use_container_width=True)

# --- TAB 3: SCENARIO MODELING ---
with tab3:
    st.header("Dynamic 'What-If' Forecasting")
    st.markdown("Stress-test the organization's P&L by dragging macroeconomic and operational factors. Watch the projected EBITDA margin update instantly.")
    
    col1, col2, col3 = st.columns(3)
    inflation_impact = col1.slider("Projected Inflation (COGS Increase %)", -10, 30, 0)
    opex_cut = col2.slider("Mandated OPEX Reduction Target (%)", 0, 40, 0)
    rev_growth = col3.slider("Sales Projection Pivot (%)", -20, 50, 0)
    
    st.markdown("---")
    
    # Run the "What-If" math on the most recent 12 months
    recent_12m = df[df['Date'] >= (df['Date'].max() - pd.DateOffset(months=12))]
    
    base_rev = recent_12m['Revenue'].sum()
    base_cogs = recent_12m['COGS'].sum()
    base_opex = recent_12m['OPEX'].sum()
    base_ebitda = recent_12m['EBITDA'].sum()
    
    sim_rev = base_rev * (1 + rev_growth/100)
    sim_cogs = base_cogs * (1 + inflation_impact/100)
    sim_opex = base_opex * (1 - opex_cut/100)
    sim_ebitda = sim_rev - sim_cogs - sim_opex
    
    # Display the simulation comparison
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Simulated Topline Revenue", f"${sim_rev/1e6:.2f}M", f"{(sim_rev - base_rev)/1e6:+.2f}M vs LTM")
    scol2.metric("Simulated OPEX Burden", f"${sim_opex/1e6:.2f}M", f"{(base_opex - sim_opex)/1e6:+.2f}M Trimmed", delta_color="inverse")
    scol3.metric("Projected EBITDA Bottom-Line", f"${sim_ebitda/1e6:.2f}M", f"{(sim_ebitda - base_ebitda)/1e6:+.2f}M Net Impact")
    
    if sim_ebitda < 0:
        st.error("🚨 WARNING: Under these macroeconomic stress parameters, the company will reach zero EBITDA liquidity and burn cash on operations.")

st.markdown("---")
st.markdown("Built by **Paras Dhand** — Advanced Analytics Portfolio")
