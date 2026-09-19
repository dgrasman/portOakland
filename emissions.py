import os
import pandas as pd

# -------------------------------------------------------------------------
# Consolidated Port of Oakland Emissions Data (2005 - 2024)
# Sources: Port of Oakland Seaport Air Emissions Inventories (2005-2024)
# -------------------------------------------------------------------------

data = [
    # --- 2005 BASELINE (Historical Method) ---
    {"Year": 2005, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 117.0, "CO": 235.0, "NOx": 2484.0, "PM10": 219.5, "PM2_5": 201.9, "DPM": 208.5, "SOx": 1413.0, "CO2e": 144141.0},
    {"Year": 2005, "Method": "Historical", "Category": "Harbor Craft", "ROG": 22.0, "CO": 83.0, "NOx": 344.8, "PM10": 13.4, "PM2_5": 12.3, "DPM": 13.4, "SOx": 3.0, "CO2e": 20053.0},
    {"Year": 2005, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 53.0, "CO": 408.0, "NOx": 766.0, "PM10": 21.7, "PM2_5": 19.9, "DPM": 21.2, "SOx": 7.0, "CO2e": 37486.0},
    {"Year": 2005, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 49.0, "CO": 149.0, "NOx": 334.0, "PM10": 15.9, "PM2_5": 14.6, "DPM": 15.9, "SOx": 2.0, "CO2e": 21676.0},
    {"Year": 2005, "Method": "Historical", "Category": "Locomotives", "ROG": 7.0, "CO": 11.0, "NOx": 76.0, "PM10": 2.0, "PM2_5": 1.8, "DPM": 2.0, "SOx": 2.0, "CO2e": 1220.0},
    {"Year": 2005, "Method": "Historical", "Category": "Other Off-Road", "ROG": 0.0, "CO": 0.0, "NOx": 0.0, "PM10": 0.0, "PM2_5": 0.0, "DPM": 0.0, "SOx": 0.0, "CO2e": 0.0},

    # --- 2012 INVENTORY (Historical Method) ---
    {"Year": 2012, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 176.0, "CO": 232.0, "NOx": 2591.0, "PM10": 66.9, "PM2_5": 62.1, "DPM": 57.4, "SOx": 289.0, "CO2e": 134332.0},
    {"Year": 2012, "Method": "Historical", "Category": "Harbor Craft", "ROG": 25.0, "CO": 95.0, "NOx": 235.0, "PM10": 9.3, "PM2_5": 9.0, "DPM": 9.3, "SOx": 0.2, "CO2e": 20377.0},
    {"Year": 2012, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 35.0, "CO": 207.0, "NOx": 413.0, "PM10": 8.0, "PM2_5": 7.4, "DPM": 7.9, "SOx": 0.6, "CO2e": 38667.0},
    {"Year": 2012, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 11.0, "CO": 43.0, "NOx": 95.0, "PM10": 2.1, "PM2_5": 1.6, "DPM": 1.5, "SOx": 0.2, "CO2e": 20697.0},
    {"Year": 2012, "Method": "Historical", "Category": "Locomotives", "ROG": 1.0, "CO": 2.0, "NOx": 19.0, "PM10": 0.5, "PM2_5": 0.4, "DPM": 0.5, "SOx": 0.01, "CO2e": 935.0},
    {"Year": 2012, "Method": "Historical", "Category": "Other Off-Road", "ROG": 1.0, "CO": 4.0, "NOx": 4.0, "PM10": 0.3, "PM2_5": 0.3, "DPM": 0.3, "SOx": 0.004, "CO2e": 370.0},

    # --- 2015 INVENTORY (Historical Method) ---
    {"Year": 2015, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 182.0, "CO": 259.0, "NOx": 2715.0, "PM10": 58.7, "PM2_5": 54.3, "DPM": 51.8, "SOx": 141.0, "CO2e": 170405.0},
    {"Year": 2015, "Method": "Historical", "Category": "Harbor Craft", "ROG": 23.0, "CO": 97.0, "NOx": 166.0, "PM10": 6.6, "PM2_5": 6.4, "DPM": 6.2, "SOx": 0.1, "CO2e": 17039.0},
    {"Year": 2015, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 43.0, "CO": 253.0, "NOx": 332.0, "PM10": 3.9, "PM2_5": 3.6, "DPM": 3.7, "SOx": 0.6, "CO2e": 32713.0},
    {"Year": 2015, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 5.0, "CO": 16.0, "NOx": 91.0, "PM10": 0.8, "PM2_5": 0.4, "DPM": 0.2, "SOx": 0.2, "CO2e": 18761.0},
    {"Year": 2015, "Method": "Historical", "Category": "Locomotives", "ROG": 0.2, "CO": 2.0, "NOx": 14.0, "PM10": 0.2, "PM2_5": 0.2, "DPM": 0.2, "SOx": 0.01, "CO2e": 645.0},
    {"Year": 2015, "Method": "Historical", "Category": "Other Off-Road", "ROG": 1.0, "CO": 12.0, "NOx": 11.0, "PM10": 0.6, "PM2_5": 0.5, "DPM": 0.6, "SOx": 0.01, "CO2e": 1191.0},

    # --- 2017 INVENTORY (Historical Method) ---
    {"Year": 2017, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 177.1, "CO": 219.3, "NOx": 2344.6, "PM10": 49.5, "PM2_5": 45.9, "DPM": 42.2, "SOx": 128.9, "CO2e": 133680.0},
    {"Year": 2017, "Method": "Historical", "Category": "Harbor Craft", "ROG": 21.0, "CO": 89.1, "NOx": 161.7, "PM10": 6.5, "PM2_5": 6.3, "DPM": 6.5, "SOx": 0.15, "CO2e": 17739.0},
    {"Year": 2017, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 18.6, "CO": 162.2, "NOx": 173.0, "PM10": 1.7, "PM2_5": 1.6, "DPM": 1.6, "SOx": 0.33, "CO2e": 35520.0},
    {"Year": 2017, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 4.7, "CO": 23.9, "NOx": 79.9, "PM10": 0.9, "PM2_5": 0.5, "DPM": 0.3, "SOx": 0.18, "CO2e": 19805.0},
    {"Year": 2017, "Method": "Historical", "Category": "Locomotives", "ROG": 0.8, "CO": 1.2, "NOx": 16.8, "PM10": 0.3, "PM2_5": 0.2, "DPM": 0.3, "SOx": 0.01, "CO2e": 703.0},
    {"Year": 2017, "Method": "Historical", "Category": "Other Off-Road", "ROG": 0.8, "CO": 40.2, "NOx": 10.5, "PM10": 0.3, "PM2_5": 0.3, "DPM": 0.3, "SOx": 0.01, "CO2e": 2228.0},

    # --- 2020 INVENTORY (Historical Method) ---
    {"Year": 2020, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 145.4, "CO": 217.1, "NOx": 1954.2, "PM10": 32.7, "PM2_5": 30.1, "DPM": 27.7, "SOx": 69.0, "CO2e": 115437.0},
    {"Year": 2020, "Method": "Historical", "Category": "Harbor Craft", "ROG": 20.9, "CO": 101.5, "NOx": 156.0, "PM10": 5.3, "PM2_5": 5.1, "DPM": 5.3, "SOx": 0.17, "CO2e": 19772.0},
    {"Year": 2020, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 39.7, "CO": 116.2, "NOx": 195.9, "PM10": 2.8, "PM2_5": 2.5, "DPM": 2.5, "SOx": 0.41, "CO2e": 44506.0},
    {"Year": 2020, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 4.7, "CO": 30.0, "NOx": 89.3, "PM10": 1.7, "PM2_5": 0.7, "DPM": 0.2, "SOx": 0.23, "CO2e": 25782.0},
    {"Year": 2020, "Method": "Historical", "Category": "Locomotives", "ROG": 0.6, "CO": 1.2, "NOx": 6.5, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.1, "SOx": 0.00, "CO2e": 491.0},
    {"Year": 2020, "Method": "Historical", "Category": "Other Off-Road", "ROG": 1.4, "CO": 40.1, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.0, "SOx": 0.01, "CO2e": 637.0},

    # --- 2023 INVENTORY (Historical Method) ---
    {"Year": 2023, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 99.0, "CO": 184.9, "NOx": 1554.3, "PM10": 29.7, "PM2_5": 27.3, "DPM": 23.0, "SOx": 62.5, "CO2e": 110680.0},
    {"Year": 2023, "Method": "Historical", "Category": "Harbor Craft", "ROG": 3.8, "CO": 22.0, "NOx": 101.4, "PM10": 1.8, "PM2_5": 1.7, "DPM": 1.8, "SOx": 0.16, "CO2e": 16705.0},
    {"Year": 2023, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 33.5, "CO": 139.8, "NOx": 179.4, "PM10": 2.6, "PM2_5": 2.4, "DPM": 2.5, "SOx": 0.40, "CO2e": 43514.0},
    {"Year": 2023, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 2.2, "CO": 32.4, "NOx": 55.1, "PM10": 1.6, "PM2_5": 0.6, "DPM": 0.1, "SOx": 0.23, "CO2e": 25426.0},
    {"Year": 2023, "Method": "Historical", "Category": "Locomotives", "ROG": 0.2, "CO": 0.4, "NOx": 3.1, "PM10": 0.05, "PM2_5": 0.04, "DPM": 0.05, "SOx": 0.00, "CO2e": 230.0},
    {"Year": 2023, "Method": "Historical", "Category": "Other Off-Road", "ROG": 1.4, "CO": 40.1, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.05, "SOx": 0.01, "CO2e": 637.0},

    # --- 2024 INVENTORY (Historical Method) ---
    {"Year": 2024, "Method": "Historical", "Category": "Ocean-Going Vessels", "ROG": 107.1, "CO": 203.0, "NOx": 1607.0, "PM10": 32.3, "PM2_5": 29.7, "DPM": 25.1, "SOx": 68.0, "CO2e": 120943.0},
    {"Year": 2024, "Method": "Historical", "Category": "Harbor Craft", "ROG": 3.3, "CO": 24.1, "NOx": 84.0, "PM10": 1.6, "PM2_5": 1.5, "DPM": 1.6, "SOx": 0.19, "CO2e": 19877.0},
    {"Year": 2024, "Method": "Historical", "Category": "Cargo Handling Equipment", "ROG": 28.7, "CO": 138.2, "NOx": 122.7, "PM10": 2.4, "PM2_5": 2.2, "DPM": 2.3, "SOx": 0.39, "CO2e": 43083.0},
    {"Year": 2024, "Method": "Historical", "Category": "Drayage Trucks", "ROG": 2.3, "CO": 33.7, "NOx": 52.3, "PM10": 1.8, "PM2_5": 0.6, "DPM": 0.1, "SOx": 0.09, "CO2e": 27837.0},
    {"Year": 2024, "Method": "Historical", "Category": "Locomotives", "ROG": 0.2, "CO": 0.4, "NOx": 2.8, "PM10": 0.04, "PM2_5": 0.04, "DPM": 0.04, "SOx": 0.00, "CO2e": 358.0},
    {"Year": 2024, "Method": "Historical", "Category": "Other Off-Road", "ROG": 1.4, "CO": 40.1, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.05, "SOx": 0.01, "CO2e": 637.0},

    # --- BEST ESTIMATE METHOD (2020, 2023, 2024) ---
    {"Year": 2020, "Method": "Best Estimate", "Category": "Ocean-Going Vessels", "ROG": 88.0, "CO": 162.0, "NOx": 1382.0, "PM10": 25.3, "PM2_5": 23.2, "DPM": 18.9, "SOx": 64.0, "CO2e": 91668.0},
    {"Year": 2020, "Method": "Best Estimate", "Category": "Harbor Craft", "ROG": 4.0, "CO": 16.0, "NOx": 111.0, "PM10": 2.1, "PM2_5": 2.0, "DPM": 2.1, "SOx": 0.2, "CO2e": 20692.0},
    {"Year": 2020, "Method": "Best Estimate", "Category": "Cargo Handling Equipment", "ROG": 40.0, "CO": 116.0, "NOx": 196.0, "PM10": 2.8, "PM2_5": 2.5, "DPM": 2.5, "SOx": 0.4, "CO2e": 44506.0},
    {"Year": 2020, "Method": "Best Estimate", "Category": "Drayage Trucks", "ROG": 5.0, "CO": 30.0, "NOx": 89.0, "PM10": 1.7, "PM2_5": 0.7, "DPM": 0.2, "SOx": 0.2, "CO2e": 25782.0},
    {"Year": 2020, "Method": "Best Estimate", "Category": "Locomotives", "ROG": 1.0, "CO": 1.0, "NOx": 6.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.1, "SOx": 0.0, "CO2e": 491.0},
    {"Year": 2020, "Method": "Best Estimate", "Category": "Other Off-Road", "ROG": 1.0, "CO": 40.0, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.0, "SOx": 0.0, "CO2e": 637.0},

    {"Year": 2023, "Method": "Best Estimate", "Category": "Ocean-Going Vessels", "ROG": 69.4, "CO": 130.2, "NOx": 1078.8, "PM10": 21.6, "PM2_5": 19.9, "DPM": 15.0, "SOx": 55.1, "CO2e": 81102.0},
    {"Year": 2023, "Method": "Best Estimate", "Category": "Harbor Craft", "ROG": 2.3, "CO": 14.7, "NOx": 64.1, "PM10": 1.2, "PM2_5": 1.1, "DPM": 1.2, "SOx": 0.1, "CO2e": 11333.0},
    {"Year": 2023, "Method": "Best Estimate", "Category": "Cargo Handling Equipment", "ROG": 33.5, "CO": 139.8, "NOx": 179.5, "PM10": 2.6, "PM2_5": 2.4, "DPM": 2.5, "SOx": 0.4, "CO2e": 43514.0},
    {"Year": 2023, "Method": "Best Estimate", "Category": "Drayage Trucks", "ROG": 2.2, "CO": 32.4, "NOx": 55.1, "PM10": 1.6, "PM2_5": 0.6, "DPM": 0.1, "SOx": 0.2, "CO2e": 25426.0},
    {"Year": 2023, "Method": "Best Estimate", "Category": "Locomotives", "ROG": 0.2, "CO": 0.4, "NOx": 3.1, "PM10": 0.05, "PM2_5": 0.04, "DPM": 0.05, "SOx": 0.0, "CO2e": 230.0},
    {"Year": 2023, "Method": "Best Estimate", "Category": "Other Off-Road", "ROG": 1.4, "CO": 40.1, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.05, "SOx": 0.01, "CO2e": 637.0},

    {"Year": 2024, "Method": "Best Estimate", "Category": "Ocean-Going Vessels", "ROG": 73.8, "CO": 139.2, "NOx": 1092.9, "PM10": 22.7, "PM2_5": 20.9, "DPM": 15.8, "SOx": 57.3, "CO2e": 85151.0},
    {"Year": 2024, "Method": "Best Estimate", "Category": "Harbor Craft", "ROG": 2.2, "CO": 16.5, "NOx": 57.1, "PM10": 1.1, "PM2_5": 1.1, "DPM": 1.1, "SOx": 0.1, "CO2e": 12838.0},
    {"Year": 2024, "Method": "Best Estimate", "Category": "Cargo Handling Equipment", "ROG": 28.7, "CO": 138.2, "NOx": 122.7, "PM10": 2.4, "PM2_5": 2.2, "DPM": 2.3, "SOx": 0.4, "CO2e": 43083.0},
    {"Year": 2024, "Method": "Best Estimate", "Category": "Drayage Trucks", "ROG": 2.3, "CO": 33.7, "NOx": 52.3, "PM10": 1.8, "PM2_5": 0.6, "DPM": 0.1, "SOx": 0.1, "CO2e": 27837.0},
    {"Year": 2024, "Method": "Best Estimate", "Category": "Locomotives", "ROG": 0.2, "CO": 0.4, "NOx": 2.8, "PM10": 0.04, "PM2_5": 0.04, "DPM": 0.04, "SOx": 0.0, "CO2e": 358.0},
    {"Year": 2024, "Method": "Best Estimate", "Category": "Other Off-Road", "ROG": 1.4, "CO": 40.1, "NOx": 3.0, "PM10": 0.1, "PM2_5": 0.1, "DPM": 0.05, "SOx": 0.01, "CO2e": 637.0},
]

df = pd.DataFrame(data)
os.makedirs("data", exist_ok=True)
df.to_csv("data/oakland_emissions_master.csv", index=False)
print("Master dataset saved to data/oakland_emissions_master.csv")