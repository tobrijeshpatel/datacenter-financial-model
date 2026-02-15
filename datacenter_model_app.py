import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Data Center Financial Model",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Make tabs more prominent */
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
    
    /* Mobile sidebar indicator */
    [data-testid="stSidebar"] > div:first-child {
        border-right: 3px solid #0068C9;
    }
    
    /* Control panel button styling */
    .stButton > button {
        font-size: 16px;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    /* Sidebar header emphasis */
    [data-testid="stSidebar"] h3 {
        color: #0068C9;
        font-size: 20px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 16px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    
    /* Reset button styling */
    .reset-button {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for default values
if 'defaults' not in st.session_state:
    st.session_state.defaults = {
        'capacity_gw': 1.0,
        'capital_cost_per_gw': 30.0,
        'gpu_nw_pct': 70,  # Store as percentage for display
        'revenue_per_gw': 12.0,
        'utilization': 70,  # Store as percentage
        'power_cost_per_kwh': 0.05,
        'pue': 1.2,
        'baseline_power': 20,  # Store as percentage
        'idle_power': 40,  # Store as percentage
        'sga_pct': 10,  # Store as percentage
        'infra_maintenance': 0.1,
        'property_tax_rate': 0.7,  # Store as percentage
        'staffing_cost': 0.05,
        'network_cost': 0.05,
        'software_compliance': 0.03,
        'depreciation_gpu_nw': 5,
        'depreciation_other': 10,
        'tax_rate': 15,  # Store as percentage
        'projection_years': 10
    }

# Initialize current values from defaults if not set
if 'current_values' not in st.session_state:
    st.session_state.current_values = st.session_state.defaults.copy()

# Function to reset to defaults
def reset_to_defaults():
    # Reset current values
    st.session_state.current_values = st.session_state.defaults.copy()
    
    # Clear all widget keys to force re-render with new values
    keys_to_delete = [
        'capacity_gw_input', 'capital_cost_input', 'gpu_nw_input',
        'revenue_input', 'utilization_input', 'power_cost_input', 'pue_input',
        'baseline_power_input', 'idle_power_input', 'sga_input', 'maintenance_input',
        'property_tax_input', 'staffing_input', 'network_input', 'software_input',
        'dep_gpu_input', 'dep_other_input', 'tax_rate_input', 'projection_input'
    ]
    
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

# Title and description
st.title("🏢 Data Center Unit Economics Model")

col_intro1, col_intro2 = st.columns([3, 1])
with col_intro1:
    st.markdown("""
    This interactive model helps you analyze the financial viability of a data center investment.
    Adjust the key assumptions in the sidebar to see real-time impact on P&L and cash flows.
    """)
with col_intro2:
    st.info("👈 Adjust assumptions  \nin sidebar")
    

# Sidebar for inputs
st.sidebar.markdown("### 📊 Control Panel")

# Reset button at the top of sidebar
if st.sidebar.button("🔄 Reset to Defaults", use_container_width=True, type="secondary"):
    reset_to_defaults()

st.sidebar.markdown("---")

# Collapsible Section 1: Capacity & Capital
with st.sidebar.expander("💰 **Capacity & Capital**", expanded=False):
    capacity_gw = st.number_input(
        "Capacity (GW)",
        min_value=0.1,
        max_value=10.0,
        value=st.session_state.current_values['capacity_gw'],
        step=0.1,
        help="Total compute capacity in gigawatts",
        key="capacity_gw_input"
    )
    
    capital_cost_per_gw = st.number_input(
        "Capital Cost ($ Billion per GW)",
        min_value=1.0,
        max_value=100.0,
        value=st.session_state.current_values['capital_cost_per_gw'],
        step=1.0,
        help="Total capital investment per GW of capacity",
        key="capital_cost_input"
    )
    
    gpu_nw_pct_display = st.slider(
        "GPU & Network Equipment",
        min_value=0,
        max_value=100,
        value=st.session_state.current_values['gpu_nw_pct'],
        step=5,
        format="%d%%",
        help="Percentage of capital cost allocated to GPU and network equipment",
        key="gpu_nw_input"
    )
    gpu_nw_pct = gpu_nw_pct_display / 100  # Convert to decimal for calculations

# Collapsible Section 2: Revenue
with st.sidebar.expander("📈 **Revenue**", expanded=False):
    revenue_per_gw = st.number_input(
        "Revenue Rate ($ Billion per GW)",
        min_value=1.0,
        max_value=50.0,
        value=st.session_state.current_values['revenue_per_gw'],
        step=0.5,
        help="Annual revenue per GW of capacity",
        key="revenue_input"
    )
    
    utilization_display = st.slider(
        "Utilization Rate",
        min_value=0,
        max_value=100,
        value=st.session_state.current_values['utilization'],
        step=5,
        format="%d%%",
        help="Expected capacity utilization",
        key="utilization_input"
    )
    utilization = utilization_display / 100  # Convert to decimal

# Collapsible Section 3: Operating Costs
with st.sidebar.expander("⚡ **Operating Costs**", expanded=False):
    power_cost_per_kwh = st.number_input(
        "Power Cost ($ per kWh)",
        min_value=0.01,
        max_value=0.20,
        value=st.session_state.current_values['power_cost_per_kwh'],
        step=0.005,
        format="%.3f",
        help="Cost of electricity per kilowatt-hour",
        key="power_cost_input"
    )
    
    pue = st.number_input(
        "PUE (Power Usage Effectiveness)",
        min_value=1.0,
        max_value=2.0,
        value=st.session_state.current_values['pue'],
        step=0.1,
        help="Ratio of total facility energy to IT equipment energy",
        key="pue_input"
    )
    
    baseline_power_display = st.slider(
        "Baseline Power",
        min_value=0,
        max_value=50,
        value=st.session_state.current_values['baseline_power'],
        step=5,
        format="%d%%",
        help="Power consumption when idle",
        key="baseline_power_input"
    )
    baseline_power = baseline_power_display / 100
    
    idle_power_display = st.slider(
        "Idle Power Factor",
        min_value=0,
        max_value=100,
        value=st.session_state.current_values['idle_power'],
        step=5,
        format="%d%%",
        help="Power factor for unused capacity",
        key="idle_power_input"
    )
    idle_power = idle_power_display / 100
    
    sga_pct_display = st.slider(
        "SG&A (% of Revenue)",
        min_value=0,
        max_value=30,
        value=st.session_state.current_values['sga_pct'],
        step=1,
        format="%d%%",
        help="Selling, general & administrative expenses",
        key="sga_input"
    )
    sga_pct = sga_pct_display / 100
    
    infra_maintenance = st.number_input(
        "Infrastructure Maintenance ($ Billion per GW)",
        min_value=0.01,
        max_value=1.0,
        value=st.session_state.current_values['infra_maintenance'],
        step=0.01,
        help="Annual maintenance costs",
        key="maintenance_input"
    )
    
    property_tax_rate_display = st.slider(
        "Property Tax Rate",
        min_value=0.0,
        max_value=3.0,
        value=st.session_state.current_values['property_tax_rate'],
        step=0.1,
        format="%.1f%%",
        help="Annual property tax as % of property value",
        key="property_tax_input"
    )
    property_tax_rate = property_tax_rate_display / 100
    
    staffing_cost = st.number_input(
        "Staffing ($ Billion per GW)",
        min_value=0.01,
        max_value=0.5,
        value=st.session_state.current_values['staffing_cost'],
        step=0.01,
        help="Annual staffing costs",
        key="staffing_input"
    )
    
    network_cost = st.number_input(
        "Network ($ Billion per GW)",
        min_value=0.01,
        max_value=0.5,
        value=st.session_state.current_values['network_cost'],
        step=0.01,
        help="Annual network costs",
        key="network_input"
    )
    
    software_compliance = st.number_input(
        "Software & Compliance ($ Billion per GW)",
        min_value=0.01,
        max_value=0.2,
        value=st.session_state.current_values['software_compliance'],
        step=0.01,
        help="Annual software and compliance costs",
        key="software_input"
    )

# Collapsible Section 4: Depreciation & Tax
with st.sidebar.expander("📉 **Depreciation & Tax**", expanded=False):
    depreciation_gpu_nw = st.number_input(
        "GPU & Network Depreciation (years)",
        min_value=1,
        max_value=15,
        value=st.session_state.current_values['depreciation_gpu_nw'],
        step=1,
        help="Useful life for GPU and network equipment",
        key="dep_gpu_input"
    )
    
    depreciation_other = st.number_input(
        "Other Assets Depreciation (years)",
        min_value=1,
        max_value=30,
        value=st.session_state.current_values['depreciation_other'],
        step=1,
        help="Useful life for buildings and infrastructure",
        key="dep_other_input"
    )
    
    tax_rate_display = st.slider(
        "Tax Rate",
        min_value=0,
        max_value=50,
        value=st.session_state.current_values['tax_rate'],
        step=1,
        format="%d%%",
        help="Corporate tax rate",
        key="tax_rate_input"
    )
    tax_rate = tax_rate_display / 100
    
    projection_years = st.number_input(
        "Projection Years",
        min_value=5,
        max_value=20,
        value=st.session_state.current_values['projection_years'],
        step=1,
        help="Number of years to project cash flows",
        key="projection_input"
    )

# Update session state with current values
st.session_state.current_values.update({
    'capacity_gw': capacity_gw,
    'capital_cost_per_gw': capital_cost_per_gw,
    'gpu_nw_pct': gpu_nw_pct_display,
    'revenue_per_gw': revenue_per_gw,
    'utilization': utilization_display,
    'power_cost_per_kwh': power_cost_per_kwh,
    'pue': pue,
    'baseline_power': baseline_power_display,
    'idle_power': idle_power_display,
    'sga_pct': sga_pct_display,
    'infra_maintenance': infra_maintenance,
    'property_tax_rate': property_tax_rate_display,
    'staffing_cost': staffing_cost,
    'network_cost': network_cost,
    'software_compliance': software_compliance,
    'depreciation_gpu_nw': depreciation_gpu_nw,
    'depreciation_other': depreciation_other,
    'tax_rate': tax_rate_display,
    'projection_years': projection_years
})

# Calculate P&L
def calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue, 
                  baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                  staffing_cost, network_cost, software_compliance, capital_cost_per_gw, 
                  gpu_nw_pct, depreciation_gpu_nw, depreciation_other):
    
    # Revenue
    revenue = revenue_per_gw * utilization * capacity_gw
    
    # Power costs (in billions)
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
    
    # Calculate payback period
    payback_years = None
    for i, cum in enumerate(cumulative_cf):
        if cum >= 0:
            payback_years = i + 1
            break
    
    if payback_years is None:
        payback_years = years
    
    return cash_flows, cumulative_cf, payback_years, operating_cf

# Perform calculations
pnl = calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue,
                   baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                   staffing_cost, network_cost, software_compliance, capital_cost_per_gw,
                   gpu_nw_pct, depreciation_gpu_nw, depreciation_other)

cash_flows, cumulative_cf, payback_years, operating_cf = calculate_cash_flows(
    pnl, capital_cost_per_gw, capacity_gw, tax_rate, projection_years)

# Main content area - KPI metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Annual Revenue",
        f"${pnl['Revenue']:.2f}B",
        help="Total annual revenue based on capacity and utilization"
    )

with col2:
    st.metric(
        "EBIT Margin",
        f"{pnl['EBIT Margin']*100:.1f}%",
        help="Operating profit margin before interest and taxes"
    )

with col3:
    payback_display = f"{payback_years:.1f} years" if payback_years < projection_years else f">{projection_years} years"
    st.metric(
        "Payback Period",
        payback_display,
        help="Time to recover initial investment"
    )

with col4:
    st.metric(
        "Operating Cash Flow",
        f"${operating_cf:.2f}B",
        help="Annual operating cash flow (EBIT after tax + depreciation)"
    )

st.markdown("---")

# Create tabs with better visibility
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 P&L Analysis", 
    "💰 Cash Flow Projection", 
    "📋 Assumptions Summary",
    "📈 Executive Summary"
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
    
    # Display P&L table
    st.dataframe(pnl_df.style.format({'Amount ($ Billion)': '{:.3f}'}), use_container_width=True)
    
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
        'Annual Cash Flow': '${:.2f}B',
        'Cumulative Cash Flow': '${:.2f}B'
    }), use_container_width=True)
    
    # Cash flow chart
    fig_cf = go.Figure()
    
    # Add annual cash flow bars
    fig_cf.add_trace(go.Bar(
        x=cf_df['Year'],
        y=cf_df['Annual Cash Flow'],
        name='Annual Cash Flow',
        marker_color='lightblue',
        yaxis='y'
    ))
    
    # Add cumulative cash flow line
    fig_cf.add_trace(go.Scatter(
        x=cf_df['Year'],
        y=cf_df['Cumulative Cash Flow'],
        name='Cumulative Cash Flow',
        mode='lines+markers',
        marker_color='darkblue',
        line=dict(width=3),
        yaxis='y'
    ))
    
    # Add zero line
    fig_cf.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    # Add payback period annotation
    if payback_years <= projection_years:
        fig_cf.add_vline(
            x=payback_years,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Payback: Year {payback_years:.0f}",
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
    
    # IRR calculation - only show if successful
    try:
        cf_for_irr = [-capital_cost_per_gw * capacity_gw] + [operating_cf] * projection_years
        irr = np.irr(cf_for_irr)
        if not np.isnan(irr) and np.isfinite(irr):
            st.info(f"**Internal Rate of Return (IRR):** {irr*100:.2f}%")
    except:
        pass  # Silently skip if IRR cannot be calculated

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
                f"{capacity_gw:.2f} GW",
                f"${capital_cost_per_gw:.1f}B",
                f"{gpu_nw_pct_display}%",
                f"${capital_cost_per_gw * capacity_gw:.2f}B"
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
                f"${pnl['Revenue']:.2f}B"
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
                f"${infra_maintenance:.2f}B",
                f"{property_tax_rate_display:.1f}%",
                f"${staffing_cost:.2f}B",
                f"${network_cost:.2f}B",
                f"${software_compliance:.2f}B"
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
        - **Total Investment:** ${capital_cost_per_gw * capacity_gw:.2f}B
        - **Capacity:** {capacity_gw:.2f} GW
        - **Utilization:** {utilization_display}%
        - **Revenue per GW:** ${revenue_per_gw:.2f}B
        """)
        
        st.markdown("### Financial Performance")
        st.markdown(f"""
        - **Annual Revenue:** ${pnl['Revenue']:.2f}B
        - **Annual EBIT:** ${pnl['EBIT']:.2f}B
        - **EBIT Margin:** {pnl['EBIT Margin']*100:.1f}%
        - **Operating Cash Flow:** ${operating_cf:.2f}B
        """)
    
    with col2:
        st.markdown("### Cost Structure")
        st.markdown(f"""
        - **Power Cost:** ${pnl['Power Cost']:.2f}B ({pnl['Power Cost']/pnl['Revenue']*100:.1f}% of revenue)
        - **SG&A:** ${pnl['SG&A']:.2f}B ({pnl['SG&A']/pnl['Revenue']*100:.1f}% of revenue)
        - **Other Operating:** ${pnl['Other Opex']:.2f}B ({pnl['Other Opex']/pnl['Revenue']*100:.1f}% of revenue)
        - **Property Tax:** ${pnl['Property Tax']:.2f}B ({pnl['Property Tax']/pnl['Revenue']*100:.1f}% of revenue)
        """)
        
        st.markdown("### Returns")
        st.markdown(f"""
        - **Payback Period:** {payback_years:.1f} years
        - **ROIC (Year 1):** {(operating_cf / (capital_cost_per_gw * capacity_gw))*100:.1f}%
        """)
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    insights = []
    
    # Profitability insights
    if pnl['EBIT Margin'] > 0.3:
        insights.append("✅ Strong profitability with EBIT margin above 30%")
    elif pnl['EBIT Margin'] < 0.1:
        insights.append("⚠️ Low profitability - consider optimizing costs or increasing utilization")
    else:
        insights.append(f"📊 EBIT margin of {pnl['EBIT Margin']*100:.1f}% is moderate")
    
    # Payback insights
    if payback_years <= 5:
        insights.append("✅ Attractive payback period under 5 years")
    elif payback_years > 10:
        insights.append("⚠️ Long payback period - may need to improve economics")
    else:
        insights.append(f"📊 Payback period of {payback_years:.1f} years is reasonable for infrastructure")
    
    # Power cost insights
    power_pct = (pnl['Power Cost'] / pnl['Revenue']) * 100
    if power_pct > 40:
        insights.append(f"⚠️ Power costs are high at {power_pct:.1f}% of revenue - consider power optimization or PPA strategies")
    elif power_pct < 10:
        insights.append(f"✅ Excellent power efficiency at {power_pct:.1f}% of revenue")
    
    # Utilization insights (utilization is already decimal 0-1)
    if utilization < 0.6:
        insights.append(f"💡 Current utilization at {utilization*100:.0f}% - improving to 70%+ could significantly boost returns")
    elif utilization >= 0.75:
        insights.append(f"✅ Strong utilization at {utilization*100:.0f}%")
    
    # Capital efficiency insight
    revenue_per_capex = pnl['Revenue'] / (capital_cost_per_gw * capacity_gw)
    if revenue_per_capex > 0.3:
        insights.append(f"✅ Good capital efficiency - generating ${revenue_per_capex:.2f} revenue per $1 invested")
    elif revenue_per_capex < 0.2:
        insights.append(f"⚠️ Low capital efficiency - only ${revenue_per_capex:.2f} revenue per $1 invested")
    
    # Display insights
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
    # Create downloadable P&L CSV
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
    # Create downloadable cash flow CSV
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
    <p style='font-size: 12px;'>Adjust assumptions in the sidebar to explore different scenarios</p>
    <p style='font-size: 12px;'>💡 Tip: Click the tabs above to explore different views</p>
</div>
""", unsafe_allow_html=True)
