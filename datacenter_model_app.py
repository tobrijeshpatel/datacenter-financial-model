import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Data Center Financial Model",
    page_icon="🏢",
    layout="wide"
)

# Title and description
st.title("🏢 Data Center Unit Economics Model")
st.markdown("""
This interactive model helps you analyze the financial viability of a data center investment.
Adjust the key assumptions in the sidebar to see real-time impact on P&L and cash flows.
""")

# Sidebar for inputs
st.sidebar.header("📊 Key Assumptions")

# Capacity and Capital
st.sidebar.subheader("Capacity & Capital")
capacity_gw = st.sidebar.number_input(
    "Capacity (GW)",
    min_value=0.1,
    max_value=10.0,
    value=1.0,
    step=0.1,
    help="Total compute capacity in gigawatts"
)

capital_cost_per_gw = st.sidebar.number_input(
    "Capital Cost ($ Billion per GW)",
    min_value=1.0,
    max_value=100.0,
    value=30.0,
    step=1.0,
    help="Total capital investment per GW of capacity"
)

gpu_nw_pct = st.sidebar.slider(
    "GPU & Network Equipment (% of CapEx)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.05,
    format="%.0f%%",
    help="Percentage of capital cost allocated to GPU and network equipment"
)

# Revenue
st.sidebar.subheader("Revenue")
revenue_per_gw = st.sidebar.number_input(
    "Revenue Rate ($ Billion per GW)",
    min_value=1.0,
    max_value=50.0,
    value=12.0,
    step=0.5,
    help="Annual revenue per GW of capacity"
)

utilization = st.sidebar.slider(
    "Utilization Rate (%)",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.05,
    format="%.0f%%",
    help="Expected capacity utilization"
)

# Operating Costs
st.sidebar.subheader("Operating Costs")
power_cost_per_kwh = st.sidebar.number_input(
    "Power Cost ($ per kWh)",
    min_value=0.01,
    max_value=0.20,
    value=0.05,
    step=0.005,
    format="%.3f",
    help="Cost of electricity per kilowatt-hour"
)

pue = st.sidebar.number_input(
    "PUE (Power Usage Effectiveness)",
    min_value=1.0,
    max_value=2.0,
    value=1.2,
    step=0.1,
    help="Ratio of total facility energy to IT equipment energy"
)

baseline_power = st.sidebar.slider(
    "Baseline Power (% of capacity)",
    min_value=0.0,
    max_value=0.5,
    value=0.2,
    step=0.05,
    format="%.0f%%",
    help="Power consumption when idle"
)

idle_power = st.sidebar.slider(
    "Idle Power Factor",
    min_value=0.0,
    max_value=1.0,
    value=0.4,
    step=0.05,
    format="%.0f%%",
    help="Power factor for unused capacity"
)

sga_pct = st.sidebar.slider(
    "SG&A (% of Revenue)",
    min_value=0.0,
    max_value=0.3,
    value=0.1,
    step=0.01,
    format="%.0f%%",
    help="Selling, general & administrative expenses"
)

infra_maintenance = st.sidebar.number_input(
    "Infrastructure Maintenance ($ Billion per GW)",
    min_value=0.01,
    max_value=1.0,
    value=0.1,
    step=0.01,
    help="Annual maintenance costs"
)

property_tax_rate = st.sidebar.slider(
    "Property Tax Rate (%)",
    min_value=0.0,
    max_value=0.03,
    value=0.007,
    step=0.001,
    format="%.1f%%",
    help="Annual property tax as % of property value"
)

staffing_cost = st.sidebar.number_input(
    "Staffing ($ Billion per GW)",
    min_value=0.01,
    max_value=0.5,
    value=0.05,
    step=0.01,
    help="Annual staffing costs"
)

network_cost = st.sidebar.number_input(
    "Network ($ Billion per GW)",
    min_value=0.01,
    max_value=0.5,
    value=0.05,
    step=0.01,
    help="Annual network costs"
)

software_compliance = st.sidebar.number_input(
    "Software & Compliance ($ Billion per GW)",
    min_value=0.01,
    max_value=0.2,
    value=0.03,
    step=0.01,
    help="Annual software and compliance costs"
)

# Depreciation and Tax
st.sidebar.subheader("Depreciation & Tax")
depreciation_gpu_nw = st.sidebar.number_input(
    "GPU & Network Depreciation (years)",
    min_value=1,
    max_value=15,
    value=5,
    step=1,
    help="Useful life for GPU and network equipment"
)

depreciation_other = st.sidebar.number_input(
    "Other Assets Depreciation (years)",
    min_value=1,
    max_value=30,
    value=10,
    step=1,
    help="Useful life for buildings and infrastructure"
)

tax_rate = st.sidebar.slider(
    "Tax Rate (%)",
    min_value=0.0,
    max_value=0.5,
    value=0.15,
    step=0.01,
    format="%.0f%%",
    help="Corporate tax rate"
)

# Projection years
projection_years = st.sidebar.number_input(
    "Projection Years",
    min_value=5,
    max_value=20,
    value=10,
    step=1,
    help="Number of years to project cash flows"
)

# Calculate P&L
def calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue, 
                  baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                  staffing_cost, network_cost, software_compliance, capital_cost_per_gw, 
                  gpu_nw_pct, depreciation_gpu_nw, depreciation_other):
    
    # Revenue
    revenue = revenue_per_gw * utilization * capacity_gw
    
    # Power costs (in billions)
    # Base electricity cost per GW at given power cost
    electricity_base = 0.438 * (power_cost_per_kwh / 0.05)  # Scale from baseline
    
    power_active = pue * utilization * capacity_gw * electricity_base
    power_idle_cost = idle_power * (1 - utilization) * capacity_gw * pue * electricity_base
    power_baseline_cost = baseline_power * capacity_gw * electricity_base
    
    total_power = power_active + power_idle_cost + power_baseline_cost
    
    # SG&A
    sga = sga_pct * revenue
    
    # Other Opex (excluding property tax which is calculated separately)
    other_opex = (infra_maintenance + staffing_cost + network_cost + software_compliance) * capacity_gw
    
    # Property tax
    property_tax = property_tax_rate * capital_cost_per_gw * capacity_gw
    
    # Depreciation
    depreciation = (capital_cost_per_gw * gpu_nw_pct / depreciation_gpu_nw + 
                   capital_cost_per_gw * (1 - gpu_nw_pct) / depreciation_other)
    
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
        payback_years = years  # Doesn't pay back within projection period
    
    return cash_flows, cumulative_cf, payback_years, operating_cf

# Perform calculations
pnl = calculate_pnl(capacity_gw, revenue_per_gw, utilization, power_cost_per_kwh, pue,
                   baseline_power, idle_power, sga_pct, infra_maintenance, property_tax_rate,
                   staffing_cost, network_cost, software_compliance, capital_cost_per_gw,
                   gpu_nw_pct, depreciation_gpu_nw, depreciation_other)

cash_flows, cumulative_cf, payback_years, operating_cf = calculate_cash_flows(
    pnl, capital_cost_per_gw, capacity_gw, tax_rate, projection_years)

# Main content area
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
    st.metric(
        "Payback Period",
        f"{payback_years:.1f} years" if payback_years < projection_years else f">{projection_years} years",
        help="Time to recover initial investment"
    )

with col4:
    st.metric(
        "Operating Cash Flow",
        f"${operating_cf:.2f}B",
        help="Annual operating cash flow (EBIT after tax + depreciation)"
    )

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["📊 P&L Analysis", "💰 Cash Flow Projection", "📈 Summary Metrics"])

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
    
    # Add payback period annotation if within projection period
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
    
    # IRR calculation
    try:
        cf_for_irr = [-capital_cost_per_gw * capacity_gw] + [operating_cf] * projection_years
        irr = np.irr(cf_for_irr)
        st.info(f"**Internal Rate of Return (IRR):** {irr*100:.2f}%")
    except:
        st.warning("Unable to calculate IRR with current assumptions")

with tab3:
    st.subheader("Executive Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Investment Overview")
        st.markdown(f"""
        - **Total Investment:** ${capital_cost_per_gw * capacity_gw:.2f}B
        - **Capacity:** {capacity_gw:.2f} GW
        - **Utilization:** {utilization*100:.0f}%
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
        total_opex = pnl['Power Cost'] + pnl['SG&A'] + pnl['Other Opex'] + pnl['Property Tax']
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
    
    if pnl['EBIT Margin'] > 0.3:
        insights.append("✅ Strong profitability with EBIT margin above 30%")
    elif pnl['EBIT Margin'] < 0.1:
        insights.append("⚠️ Low profitability - consider optimizing costs or increasing utilization")
    
    if payback_years <= 5:
        insights.append("✅ Attractive payback period under 5 years")
    elif payback_years > 10:
        insights.append("⚠️ Long payback period - may need to improve economics")
    
    if pnl['Power Cost'] / pnl['Revenue'] > 0.4:
        insights.append("⚠️ Power costs are high - consider power optimization or PPA strategies")
    
    if utilization < 0.6:
        insights.append("💡 Low utilization - improving to 70%+ could significantly boost returns")
    
    for insight in insights:
        st.markdown(f"- {insight}")

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
</div>
""", unsafe_allow_html=True)
