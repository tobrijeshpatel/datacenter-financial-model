import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Page configuration - NO SIDEBAR
st.set_page_config(
    page_title="Data Center Financial Model",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar completely
)

# Custom CSS for new layout
st.markdown("""
<style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sticky KPI section */
    .sticky-kpi {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Dark mode support for sticky KPI */
    [data-testid="stAppViewContainer"][data-theme="dark"] .sticky-kpi {
        background-color: #0e1117;
    }
    
    /* Tab styling - dark grey theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #262730;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #3d3d4a;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 16px;
        border: 2px solid #3d3d4a;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0068C9;
        color: white;
        border: 2px solid #0068C9;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 18px;
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 12px;
    }
    
    [data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Control panel container */
    .control-panel {
        background-color: #fafafa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Reset button styling */
    .stButton > button {
        font-weight: 600;
        border-radius: 8px;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.4rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 14px;
            padding: 8px 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for default values
if 'defaults' not in st.session_state:
    st.session_state.defaults = {
        'capacity_gw': 1.0,
        'capital_cost_per_gw': 30.0,
        'gpu_nw_pct': 70,
        'revenue_per_gw': 12.0,
        'utilization': 70,
        'power_cost_per_kwh': 0.05,
        'pue': 1.2,
        'baseline_power': 20,
        'idle_power': 40,
        'sga_pct': 10,
        'infra_maintenance': 0.1,
        'property_tax_rate': 0.7,
        'staffing_cost': 0.05,
        'network_cost': 0.05,
        'software_compliance': 0.03,
        'depreciation_gpu_nw': 5,
        'depreciation_other': 10,
        'tax_rate': 15,
        'projection_years': 10
    }

# Initialize widget values in session state if not present
for key, value in st.session_state.defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Function to reset to defaults
def reset_to_defaults():
    for key, value in st.session_state.defaults.items():
        st.session_state[key] = value

# Header
st.title("🏢 Data Center Unit Economics Model")
st.markdown("""
Analyze the financial viability of AI infrastructure investments with real-time P&L, 
cash flow projections, and payback calculations.
""")

st.markdown("---")

# Get all input values
capacity_gw = st.session_state.capacity_gw
capital_cost_per_gw = st.session_state.capital_cost_per_gw
gpu_nw_pct_display = st.session_state.gpu_nw_pct
gpu_nw_pct = gpu_nw_pct_display / 100
revenue_per_gw = st.session_state.revenue_per_gw
utilization_display = st.session_state.utilization
utilization = utilization_display / 100
power_cost_per_kwh = st.session_state.power_cost_per_kwh
pue = st.session_state.pue
baseline_power_display = st.session_state.baseline_power
baseline_power = baseline_power_display / 100
idle_power_display = st.session_state.idle_power
idle_power = idle_power_display / 100
sga_pct_display = st.session_state.sga_pct
sga_pct = sga_pct_display / 100
infra_maintenance = st.session_state.infra_maintenance
property_tax_rate_display = st.session_state.property_tax_rate
property_tax_rate = property_tax_rate_display / 100
staffing_cost = st.session_state.staffing_cost
network_cost = st.session_state.network_cost
software_compliance = st.session_state.software_compliance
depreciation_gpu_nw = st.session_state.depreciation_gpu_nw
depreciation_other = st.session_state.depreciation_other
tax_rate_display = st.session_state.tax_rate
tax_rate = tax_rate_display / 100
projection_years = st.session_state.projection_years

# Calculate P&L
def calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue, 
                  baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                  staffing_cost, network_cost, software_compliance, capital_cost_per_gw, 
                  gpu_nw_pct, depreciation_gpu_nw, depreciation_other):
    
    # Revenue
    revenue = revenue_per_gw * utilization * capacity_gw
    
    # Power costs
    electricity_base = 0.438 * (power_cost_per_kwh / 0.05)
    power_active = pue * utilization * capacity_gw * electricity_base
    power_idle_cost = idle_power * (1 - utilization) * capacity_gw * pue * electricity_base
    power_baseline_cost = baseline_power * capacity_gw * electricity_base
    total_power = power_active + power_idle_cost + power_baseline_cost
    
    # SG&A
    sga = sga_pct * revenue
    
    # Other Opex
    other_opex = (infra_maintenance + staffing_cost + network_cost + software_compliance) * capacity_gw
    
    # Property tax
    property_tax = property_tax_rate * capital_cost_per_gw * capacity_gw
    
    # Depreciation
    depreciation = (capital_cost_per_gw * gpu_nw_pct / depreciation_gpu_nw + 
                   capital_cost_per_gw * (1 - gpu_nw_pct) / depreciation_other) * capacity_gw
    
    # EBIT
    ebit = revenue - total_power - sga - other_opex - property_tax - depreciation
    ebit_margin = ebit / revenue if revenue > 0 else 0
    
    return {
        'Revenue': revenue,
        'Power Cost': total_power,
        'SG&A': sga,
        'Other Opex': other_opex,
        'Property Tax': property_tax,
        'Depreciation': depreciation,
        'EBIT': ebit,
        'EBIT Margin': ebit_margin
    }

# Calculate cash flows
def calculate_cash_flows(pnl_dict, capital_cost_per_gw, capacity_gw, tax_rate, years):
    initial_investment = capital_cost_per_gw * capacity_gw
    operating_cf = pnl_dict['EBIT'] * (1 - tax_rate) + pnl_dict['Depreciation']
    
    # Simple payback: Total CapEx / Annual OCF
    payback_years = initial_investment / operating_cf if operating_cf > 0 else years
    
    cash_flows = []
    cumulative_cf = []
    cum_cf = -initial_investment
    
    for year in range(years):
        if year == 0:
            cf = -initial_investment + operating_cf
        else:
            cf = operating_cf
        
        cum_cf += cf
        cash_flows.append(cf)
        cumulative_cf.append(cum_cf)
    
    return cash_flows, cumulative_cf, payback_years, operating_cf

# Perform calculations
pnl = calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue,
                   baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                   staffing_cost, network_cost, software_compliance, capital_cost_per_gw,
                   gpu_nw_pct, depreciation_gpu_nw, depreciation_other)

cash_flows, cumulative_cf, payback_years, operating_cf = calculate_cash_flows(
    pnl, capital_cost_per_gw, capacity_gw, tax_rate, projection_years)

# STICKY KPI SECTION
st.markdown('<div class="sticky-kpi">', unsafe_allow_html=True)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "Revenue",
        f"${pnl['Revenue']:.1f}B",
        help="Annual revenue"
    )

with kpi2:
    st.metric(
        "EBIT Margin",
        f"{pnl['EBIT Margin']*100:.1f}%",
        help="Operating profit margin"
    )

with kpi3:
    st.metric(
        "Payback",
        f"{payback_years:.1f}yr",
        help="Years to recover investment"
    )

with kpi4:
    st.metric(
        "OCF",
        f"${operating_cf:.1f}B",
        help="Operating cash flow"
    )
st.markdown('</div>', unsafe_allow_html=True)

# CONTROL PANEL SECTION
st.markdown("## ⚙️ Adjust Assumptions")

col_reset1, col_reset2 = st.columns([3, 1])
with col_reset2:
    if st.button("🔄 Reset to Defaults", use_container_width=True, type="secondary"):
        reset_to_defaults()
        st.rerun()

with st.expander("💰 **Capacity & Capital**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Capacity (GW)",
            min_value=0.1,
            max_value=10.0,
            step=0.1,
            help="Total compute capacity in gigawatts",
            key="capacity_gw"
        )
        
        st.number_input(
            "Capital Cost ($ Billion per GW)",
            min_value=1.0,
            max_value=100.0,
            step=1.0,
            help="Total capital investment per GW of capacity",
            key="capital_cost_per_gw"
        )
    
    with col2:
        st.slider(
            "GPU & Network Equipment",
            min_value=0,
            max_value=100,
            step=5,
            format="%d%%",
            help="Percentage of capital cost allocated to GPU and network equipment",
            key="gpu_nw_pct"
        )

with st.expander("📈 **Revenue**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Revenue Rate ($ Billion per GW)",
            min_value=1.0,
            max_value=50.0,
            step=0.5,
            help="Annual revenue per GW of capacity",
            key="revenue_per_gw"
        )
    
    with col2:
        st.slider(
            "Utilization Rate",
            min_value=0,
            max_value=100,
            step=5,
            format="%d%%",
            help="Expected capacity utilization",
            key="utilization"
        )

with st.expander("⚡ **Operating Costs**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Power Cost ($ per kWh)",
            min_value=0.01,
            max_value=0.20,
            step=0.005,
            format="%.3f",
            help="Cost of electricity per kilowatt-hour",
            key="power_cost_per_kwh"
        )
        
        st.number_input(
            "PUE (Power Usage Effectiveness)",
            min_value=1.0,
            max_value=2.0,
            step=0.1,
            help="Ratio of total facility energy to IT equipment energy",
            key="pue"
        )
        
        st.slider(
            "Baseline Power",
            min_value=0,
            max_value=50,
            step=5,
            format="%d%%",
            help="Power consumption when idle",
            key="baseline_power"
        )
        
        st.slider(
            "Idle Power Factor",
            min_value=0,
            max_value=100,
            step=5,
            format="%d%%",
            help="Power factor for unused capacity",
            key="idle_power"
        )
        
        st.slider(
            "SG&A (% of Revenue)",
            min_value=0,
            max_value=30,
            step=1,
            format="%d%%",
            help="Selling, general & administrative expenses",
            key="sga_pct"
        )
    
    with col2:
        st.number_input(
            "Infrastructure Maintenance ($ Billion per GW)",
            min_value=0.01,
            max_value=1.0,
            step=0.01,
            help="Annual maintenance costs",
            key="infra_maintenance"
        )
        
        st.slider(
            "Property Tax Rate",
            min_value=0.0,
            max_value=3.0,
            step=0.1,
            format="%.1f%%",
            help="Annual property tax as % of property value",
            key="property_tax_rate"
        )
        
        st.number_input(
            "Staffing ($ Billion per GW)",
            min_value=0.01,
            max_value=0.5,
            step=0.01,
            help="Annual staffing costs",
            key="staffing_cost"
        )
        
        st.number_input(
            "Network ($ Billion per GW)",
            min_value=0.01,
            max_value=0.5,
            step=0.01,
            help="Annual network costs",
            key="network_cost"
        )
        
        st.number_input(
            "Software & Compliance ($ Billion per GW)",
            min_value=0.01,
            max_value=0.2,
            step=0.01,
            help="Annual software and compliance costs",
            key="software_compliance"
        )

with st.expander("📉 **Depreciation & Tax**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "GPU & Network Depreciation (years)",
            min_value=1,
            max_value=15,
            step=1,
            help="Useful life for GPU and network equipment",
            key="depreciation_gpu_nw"
        )
        
        st.number_input(
            "Other Assets Depreciation (years)",
            min_value=1,
            max_value=30,
            step=1,
            help="Useful life for buildings and infrastructure",
            key="depreciation_other"
        )
    
    with col2:
        st.slider(
            "Tax Rate",
            min_value=0,
            max_value=50,
            step=1,
            format="%d%%",
            help="Corporate tax rate",
            key="tax_rate"
        )
        
        st.number_input(
            "Projection Years",
            min_value=5,
            max_value=20,
            step=1,
            help="Number of years to project cash flows",
            key="projection_years"
        )

st.markdown("---")

# RESULTS TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 P&L Analysis", 
    "💰 Cash Flow", 
    "📋 Assumptions",
    "📈 Summary"
])

with tab1:
    st.subheader("Profit & Loss Statement")
    
    # Create P&L dataframe
    pnl_df = pd.DataFrame({
        'Item': ['Revenue', 'Power Cost', 'SG&A', 'Other Opex', 'Property Tax', 'Depreciation', 'EBIT'],
        'Amount ($ Billion)': [
            pnl['Revenue'],
            -pnl['Power Cost'],
            -pnl['SG&A'],
            -pnl['Other Opex'],
            -pnl['Property Tax'],
            -pnl['Depreciation'],
            pnl['EBIT']
        ]
    })
    
    st.dataframe(pnl_df.style.format({'Amount ($ Billion)': '{:.1f}'}), use_container_width=True)
    
    # P&L Waterfall Chart
    st.subheader("Revenue to EBIT Waterfall")
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=pnl_df['Item'],
        y=pnl_df['Amount ($ Billion)'],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#EF553B"}},
        increasing={"marker": {"color": "#00CC96"}},
        totals={"marker": {"color": "#636EFA"}}
    ))
    
    fig_waterfall.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="",
        yaxis_title="$ Billions"
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Cost breakdown pie chart
    st.subheader("Operating Cost Breakdown")
    
    cost_breakdown = pd.DataFrame({
        'Category': ['Power Cost', 'SG&A', 'Other Opex', 'Property Tax'],
        'Amount': [
            pnl['Power Cost'],
            pnl['SG&A'],
            pnl['Other Opex'],
            pnl['Property Tax']
        ]
    })
    
    fig_pie = px.pie(
        cost_breakdown,
        values='Amount',
        names='Category',
        title='Operating Expenses Distribution',
        hole=0.4
    )
    
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.subheader("Cash Flow Projection")
    
    # Create cash flow dataframe
    years_list = list(range(1, projection_years + 1))
    cf_df = pd.DataFrame({
        'Year': years_list,
        'Annual Cash Flow': cash_flows,
        'Cumulative Cash Flow': cumulative_cf
    })
    
    st.dataframe(cf_df.style.format({
        'Annual Cash Flow': '${:.1f}B',
        'Cumulative Cash Flow': '${:.1f}B'
    }), use_container_width=True)
    
    # Cash flow chart
    fig_cf = go.Figure()
    
    fig_cf.add_trace(go.Bar(
        x=cf_df['Year'],
        y=cf_df['Annual Cash Flow'],
        name='Annual Cash Flow',
        marker_color='lightblue',
        yaxis='y'
    ))
    
    fig_cf.add_trace(go.Scatter(
        x=cf_df['Year'],
        y=cf_df['Cumulative Cash Flow'],
        name='Cumulative Cash Flow',
        mode='lines+markers',
        marker_color='darkblue',
        line=dict(width=3),
        yaxis='y'
    ))
    
    fig_cf.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    if payback_years <= projection_years:
        fig_cf.add_vline(
            x=payback_years,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Payback: Year {payback_years:.1f}",
            annotation_position="top"
        )
    
    fig_cf.update_layout(
        title="Cash Flow Analysis with Payback Period",
        xaxis_title="Year",
        yaxis_title="$ Billions",
        height=500,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_cf, use_container_width=True)
    
    # IRR calculation
    try:
        cf_for_irr = [-capital_cost_per_gw * capacity_gw] + [operating_cf] * projection_years
        irr = np.irr(cf_for_irr)
        if not np.isnan(irr) and np.isfinite(irr):
            st.info(f"**Internal Rate of Return (IRR):** {irr*100:.2f}%")
    except:
        pass

with tab3:
    st.subheader("Current Assumptions Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Capacity & Capital")
        assumptions_df1 = pd.DataFrame({
            'Parameter': [
                'Capacity',
                'Capital Cost per GW',
                'GPU & Network Equipment',
                'Total Investment'
            ],
            'Value': [
                f"{capacity_gw:.1f} GW",
                f"${capital_cost_per_gw:.1f}B",
                f"{gpu_nw_pct_display}%",
                f"${capital_cost_per_gw * capacity_gw:.1f}B"
            ]
        })
        st.dataframe(assumptions_df1, use_container_width=True, hide_index=True)
        
        st.markdown("#### 📈 Revenue")
        assumptions_df2 = pd.DataFrame({
            'Parameter': [
                'Revenue Rate per GW',
                'Utilization Rate',
                'Annual Revenue'
            ],
            'Value': [
                f"${revenue_per_gw:.1f}B",
                f"{utilization_display}%",
                f"${pnl['Revenue']:.1f}B"
            ]
        })
        st.dataframe(assumptions_df2, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### ⚡ Operating Costs")
        assumptions_df3 = pd.DataFrame({
            'Parameter': [
                'Power Cost per kWh',
                'PUE',
                'Baseline Power',
                'Idle Power',
                'SG&A',
                'Maintenance per GW',
                'Property Tax Rate',
                'Staffing per GW',
                'Network per GW',
                'Software & Compliance'
            ],
            'Value': [
                f"${power_cost_per_kwh:.3f}",
                f"{pue:.1f}",
                f"{baseline_power_display}%",
                f"{idle_power_display}%",
                f"{sga_pct_display}% of revenue",
                f"${infra_maintenance:.1f}B",
                f"{property_tax_rate_display:.1f}%",
                f"${staffing_cost:.1f}B",
                f"${network_cost:.1f}B",
                f"${software_compliance:.1f}B"
            ]
        })
        st.dataframe(assumptions_df3, use_container_width=True, hide_index=True)
        
        st.markdown("#### 📉 Depreciation & Tax")
        assumptions_df4 = pd.DataFrame({
            'Parameter': [
                'GPU & Network Depreciation',
                'Other Assets Depreciation',
                'Tax Rate',
                'Projection Years'
            ],
            'Value': [
                f"{depreciation_gpu_nw} years",
                f"{depreciation_other} years",
                f"{tax_rate_display}%",
                f"{projection_years} years"
            ]
        })
        st.dataframe(assumptions_df4, use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Investment Overview")
        st.markdown(f"""
        - **Total Investment:** ${capital_cost_per_gw * capacity_gw:.1f}B
        - **Capacity:** {capacity_gw:.1f} GW
        - **Utilization:** {utilization_display}%
        - **Revenue per GW:** ${revenue_per_gw:.1f}B
        """)
        
        st.markdown("### Financial Performance")
        st.markdown(f"""
        - **Annual Revenue:** ${pnl['Revenue']:.1f}B
        - **Annual EBIT:** ${pnl['EBIT']:.1f}B
        - **EBIT Margin:** {pnl['EBIT Margin']*100:.1f}%
        - **Operating Cash Flow:** ${operating_cf:.1f}B
        """)
    
    with col2:
        st.markdown("### Cost Structure")
        st.markdown(f"""
        - **Power Cost:** ${pnl['Power Cost']:.1f}B ({pnl['Power Cost']/pnl['Revenue']*100:.1f}% of revenue)
        - **SG&A:** ${pnl['SG&A']:.1f}B ({pnl['SG&A']/pnl['Revenue']*100:.1f}% of revenue)
        - **Other Operating:** ${pnl['Other Opex']:.1f}B ({pnl['Other Opex']/pnl['Revenue']*100:.1f}% of revenue)
        - **Property Tax:** ${pnl['Property Tax']:.1f}B ({pnl['Property Tax']/pnl['Revenue']*100:.1f}% of revenue)
        """)
        
        st.markdown("### Returns")
        st.markdown(f"""
        - **Payback Period:** {payback_years:.1f} years
        - **ROIC (Year 1):** {(operating_cf / (capital_cost_per_gw * capacity_gw))*100:.1f}%
        """)
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    insights = []
    
    if pnl['EBIT Margin'] > 0.3:
        insights.append("✅ Strong profitability with EBIT margin above 30%")
    elif pnl['EBIT Margin'] < 0.1:
        insights.append("⚠️ Low profitability - consider optimizing costs or increasing utilization")
    else:
        insights.append(f"📊 EBIT margin of {pnl['EBIT Margin']*100:.1f}% is moderate")
    
    if payback_years <= 5:
        insights.append("✅ Attractive payback period under 5 years")
    elif payback_years > 10:
        insights.append("⚠️ Long payback period - may need to improve economics")
    else:
        insights.append(f"📊 Payback period of {payback_years:.1f} years is reasonable for infrastructure")
    
    power_pct = (pnl['Power Cost'] / pnl['Revenue']) * 100
    if power_pct > 40:
        insights.append(f"⚠️ Power costs are high at {power_pct:.1f}% of revenue - consider power optimization")
    elif power_pct < 10:
        insights.append(f"✅ Excellent power efficiency at {power_pct:.1f}% of revenue")
    
    if utilization < 0.6:
        insights.append(f"💡 Current utilization at {utilization*100:.0f}% - improving to 70%+ could boost returns")
    elif utilization >= 0.75:
        insights.append(f"✅ Strong utilization at {utilization*100:.0f}%")
    
    revenue_per_capex = pnl['Revenue'] / (capital_cost_per_gw * capacity_gw)
    if revenue_per_capex > 0.3:
        insights.append(f"✅ Good capital efficiency - generating ${revenue_per_capex:.2f} revenue per $1 invested")
    elif revenue_per_capex < 0.2:
        insights.append(f"⚠️ Low capital efficiency - only ${revenue_per_capex:.2f} revenue per $1 invested")
    
    if insights:
        for insight in insights:
            st.markdown(f"- {insight}")
    else:
        st.markdown("- 📊 Adjust assumptions to see insights")

# Download section
st.markdown("---")
st.subheader("📥 Export Results")

col1, col2 = st.columns(2)

with col1:
    pnl_export = pd.DataFrame({
        'Metric': list(pnl.keys()),
        'Value': list(pnl.values())
    })
    
    csv_pnl = pnl_export.to_csv(index=False)
    st.download_button(
        label="Download P&L (CSV)",
        data=csv_pnl,
        file_name="datacenter_pnl.csv",
        mime="text/csv"
    )

with col2:
    csv_cf = cf_df.to_csv(index=False)
    st.download_button(
        label="Download Cash Flow (CSV)",
        data=csv_cf,
        file_name="datacenter_cashflow.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>Data Center Financial Model | Built with Streamlit</p>
    <p style='font-size: 12px;'>Interactive unit economics for AI infrastructure investment analysis</p>
</div>
""", unsafe_allow_html=True)
