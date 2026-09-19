import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Port of Oakland Emissions Dashboard",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/oakland_emissions_master.csv")
    return df

df = load_data()

# Sidebar Navigation & Global Filters
st.sidebar.title("Navigation & Parameters")
st.sidebar.markdown(
    "Data synthesized from official [Port of Oakland Seaport Air Emissions Inventories]"
    "(https://www.portofoakland.com/environment/environmental-stewardship/seaport-air-emissions-inventory/) "
    "and [CARB](https://ww2.arb.ca.gov/) methodologies."
)

method = st.sidebar.radio(
    "Select Methodological Paradigm:",
    options=["Historical", "Best Estimate"],
    help=(
        "Historical: Constant 2005 modeling assumptions (used to track MAQIP goals).\n"
        "Best Estimate: Current CARB guidance using AIS speed profiles & empirical shore power."
    )
)

pollutant = st.sidebar.selectbox(
    "Select Emission Metric:",
    options=["DPM", "NOx", "SOx", "PM10", "PM2_5", "ROG", "CO", "CO2e"],
    index=0
)

# Filter DataFrame
filtered_df = df[df["Method"] == method].copy()

st.title("Port of Oakland Seaport Emissions Dashboard")
st.caption(f"Visualizing **{pollutant}** trends ({method} Estimation Methodology)")

# KPI Metrics Panel (Tracking against 2005 Baseline for Historical)
if method == "Historical":
    base_year_df = filtered_df[filtered_df["Year"] == 2005]
    latest_year_df = filtered_df[filtered_df["Year"] == 2024]
    
    base_val = base_year_df[pollutant].sum()
    latest_val = latest_year_df[pollutant].sum()
    pct_change = ((latest_val - base_val) / base_val) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("2005 Baseline Total", f"{base_val:,.1f} tons")
    col2.metric("2024 Total", f"{latest_val:,.1f} tons", delta=f"{pct_change:.1f}%", delta_color="inverse")
    
    # Check MAQIP Milestones
    if pollutant == "DPM":
        status = "Achieved (Goal: -85%)" if pct_change <= -85 else "In Progress"
        col3.metric("MAQIP 2020 Target", status)
    elif pollutant == "NOx":
        status = "Achieved (Goal: -34%)" if pct_change <= -34 else "In Progress"
        col3.metric("MAQIP 2020 Target", status)
    elif pollutant == "SOx":
        status = "Achieved (Goal: -95%)" if pct_change <= -95 else "In Progress"
        col3.metric("MAQIP 2020 Target", status)
    else:
        col3.metric("Status", "Tracked Criteria/GHG")

# Main Visualizations
st.markdown("---")
tab1, tab2 = st.tabs(["Stacked Sector Trends", "Raw Data & Aggregations"])

with tab1:
    fig = px.bar(
        filtered_df,
        x="Year",
        y=pollutant,
        color="Category",
        title=f"Annual {pollutant} Emissions by Source Category ({method} Method)",
        labels={pollutant: f"{pollutant} (tons/year)", "Year": "Inventory Year"},
        barmode="stack",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig.update_layout(xaxis=dict(type='category'), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader(f"Summary Table: {pollutant} (tons/year)")
    pivot_df = filtered_df.pivot_table(
        index="Category", 
        columns="Year", 
        values=pollutant, 
        aggfunc="sum", 
        margins=True, 
        margins_name="Total Port Emissions"
    )
    st.dataframe(pivot_df.style.format("{:,.2f}"))