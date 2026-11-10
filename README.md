# Port of Oakland Emissions Dashboard

An interactive web application built with Streamlit and Plotly to visualize and explore historical Seaport Air Emissions Inventories for the Port of Oakland from 2005 to 2020. 

## Features

*   **Global Filters:** View data by specific pollutants (DPM, NOx, SOx, PM10, PM2.5, ROG, CO, CO2e) and modeling methodologies (Historical vs Best Estimate).
*   **KPI Metrics:** Track emissions progress against the 2005 baseline and view emissions intensity per TEU.
*   **Sector Trends:** View stacked bar charts of emissions broken down by major source categories (Ocean-Going Vessels, Harbor Craft, Cargo Handling Equipment, Drayage Trucks, Locomotives, and Other Off-Road Equipment).
*   **Deep Dive Analytics:** Drill down into specific sectors:
    *   **Port Activity Trends:** Analyze changes in TEU throughput vs. Vessel Calls and Truck Trips.
    *   **Ocean-Going Vessels (OGV):** View emissions categorized by operating modes (Cruise, Reduced Speed Zone, Maneuvering, Berth, Shifts, Anchorage).
    *   **Drayage Trucks:** Break down truck emissions by operating modes (Surface Roads, Gate Idling, In-Terminal Idling, In-Terminal Driving).

## Data Pipeline

The data is sourced directly from the official Port of Oakland Seaport Air Emissions Inventories.

1.  Run the generation script to compile the master dataset and subcategory metrics into the `data/` directory:
    ```bash
    python3 emissions.py
    ```
2.  The script will generate the following files:
    *   `oakland_emissions_master.csv`
    *   `activity_metrics.csv`
    *   `ogv_modes.csv`
    *   `truck_modes.csv`

## Vessel Particulars & VesselAPI Integration

Live AIS stream data records arriving vessels in `data/port_traffic.db`. You can enrich vessel particulars using [VesselAPI](https://vesselapi.com) with your `VESSEL_MMSI_API_KEY` (configured in `.env`):

- **Gross Tonnage (GT)**: Exact GT measure of overall vessel internal volume.
- **Refined TEU Capacity**: Calculated using naval architectural container ship regression models or verified VesselAPI registry metrics (replaces coarse length archetypes).
- **Auxiliary Engine Specs**:
  - `aux_engine_capacity_kw`: Estimated total installed auxiliary diesel generator capacity.
  - `aux_engine_kw`: Average at-berth operating electrical load (hotel + reefer) based on CARB OGV Inventory methodologies.
  - `main_engine_kw`: Installed main engine power.
- **Dual-Fuel & Fuel Capability**: Automatic detection of dual-fuel capability (e.g., LNG Dual-Fuel, Methanol Dual-Fuel) based on engine model codes (`ME-GI`, `X-DF`, `ME-LGIM`, etc.) and EU MRV emissions reporting.

### Running Batch Enrichment
```bash
# Enrich the 20 most frequent Port of Oakland callers that haven't been enriched yet
python3 vessel_api_service.py 20
```

*Note: Only vessels that have berthed (moored) at the Port of Oakland are enriched, both in the batch above and automatically by `ais_service.py` when a ship moors. The script tracks your remaining API monthly quota (`X-Ratelimit-Remaining`) and halts before quota exhaustion. Already-enriched vessels are cached in SQLite to prevent duplicate calls.*

All of this data lives in the `vessel_particulars` table. `is_oakland_berth` / `oakland_berth_count` show which vessels actually berth at Oakland, and `GT` is only filled with VesselAPI-verified values.

## Running the Application Locally

1.  Ensure you have the requirements installed:
    ```bash
    pip install -r requirements.txt
    ```
2.  Start the Streamlit development server:
    ```bash
    streamlit run streamlit_app.py
    ```

## Deployment

This app is designed to be easily deployed to Streamlit Community Cloud. Ensure all generated CSV files in the `data/` directory are committed and pushed to your GitHub repository, as the cloud environment relies on these static files.

