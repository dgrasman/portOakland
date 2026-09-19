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
