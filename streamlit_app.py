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
    try:
        df_act = pd.read_csv("data/activity_metrics.csv")
        df_ogv = pd.read_csv("data/ogv_modes.csv")
        df_truck = pd.read_csv("data/truck_modes.csv")
    except FileNotFoundError:
        df_act, df_ogv, df_truck = None, None, None
    return df, df_act, df_ogv, df_truck

df, df_act, df_ogv, df_truck = load_data()

# Sidebar Navigation & Global Filters
st.sidebar.title("Parameters")
st.sidebar.markdown(
    "Data synthesized from official [Port of Oakland Seaport Air Emissions Inventories]"
    "(https://www.portofoakland.com/environment/environmental-stewardship/seaport-air-emissions-inventory/) "
    "and [CARB](https://ww2.arb.ca.gov/) methodologies."
)

method = st.sidebar.radio(
    "Methodology",
    options=["Historical", "Best Estimate"],
    help=(
        "Historical: Constant 2005 modeling assumptions (used to track MAQIP goals).\n"
        "Best Estimate: Current CARB guidance using AIS speed profiles & empirical shore power."
    )
)

metric_labels = {
    "DPM": "Diesel Particulate Matter (DPM)",
    "ROG": "Reactive Organic Gases (ROG)"
}

pollutant = st.sidebar.selectbox(
    "Metric",
    options=["DPM", "NOx", "SOx", "PM10", "PM2_5", "ROG", "CO", "CO2e"],
    format_func=lambda x: metric_labels.get(x, x),
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
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        xaxis=dict(type='category'), 
        hovermode="x unified",
        template="simple_white"
    )
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

# Drill-Down Analytics
if df_act is not None:
    st.markdown("---")
    st.subheader("Deep Dive Analytics")
    
    analysis_category = st.selectbox(
        "Select Category for In-Depth Analysis:", 
        ["Activity Metrics", "Ocean-Going Vessels", "Drayage Trucks"]
    )
    
    if analysis_category == "Activity Metrics":
        st.markdown(f"#### Port Activity Trends")
        # Dual axis or normalized chart for TEU vs others
        fig_act = px.line(
            df_act, 
            x="Year", 
            y=["TEU", "TruckTrips"], 
            title="TEU Throughput vs Truck Trips",
            template="simple_white",
            color_discrete_sequence=["#1f2937", "#9ca3af"]
        )
        st.plotly_chart(fig_act, use_container_width=True)
        
        fig_calls = px.line(
            df_act,
            x="Year",
            y="VesselCalls",
            title="Ocean-Going Vessel Calls",
            template="simple_white",
            color_discrete_sequence=["#374151"]
        )
        st.plotly_chart(fig_calls, use_container_width=True)
        
    elif analysis_category == "Ocean-Going Vessels":
        st.markdown(f"#### OGV **{pollutant}** Emissions by Operating Mode")
        fig_ogv = px.bar(
            df_ogv, 
            x="Year", 
            y=pollutant, 
            color="Mode", 
            barmode="stack", 
            title=f"OGV {pollutant} by Mode",
            template="simple_white",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_ogv, use_container_width=True)
        
    elif analysis_category == "Drayage Trucks":
        st.markdown(f"#### Truck **{pollutant}** Emissions by Operating Mode")
        fig_truck = px.bar(
            df_truck, 
            x="Year", 
            y=pollutant, 
            color="Mode", 
            barmode="stack", 
            title=f"Drayage Truck {pollutant} by Mode",
            template="simple_white",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_truck, use_container_width=True)