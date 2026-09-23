import os
import pandas as pd


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

activity_data = [
    {"Year": 2005, "TEU": 2273990, "VesselCalls": 1916, "TruckTrips": 2620483, "ShorePowerPluginRate": 0.0, "RenewableEnergyPercent": 20.0},
    {"Year": 2012, "TEU": 2344392, "VesselCalls": 1812, "TruckTrips": 2339792, "ShorePowerPluginRate": 0.0, "RenewableEnergyPercent": 33.0},
    {"Year": 2015, "TEU": 2277521, "VesselCalls": 1393, "TruckTrips": 2081130, "ShorePowerPluginRate": 50.0, "RenewableEnergyPercent": 40.0},
    {"Year": 2017, "TEU": 2420837, "VesselCalls": 1596, "TruckTrips": 2081932, "ShorePowerPluginRate": 68.0, "RenewableEnergyPercent": 50.0},
    {"Year": 2020, "TEU": 2461262, "VesselCalls": 1231, "TruckTrips": 2892052, "ShorePowerPluginRate": 80.0, "RenewableEnergyPercent": 65.0},
]

ogv_modes = [
    {"Year": 2005, "Mode": "Cruise", "ROG": 16, "CO": 46, "NOx": 588, "PM10": 52.4, "PM2_5": 0, "DPM": 52.4, "SOx": 383, "CO2e": 0},
    {"Year": 2005, "Mode": "RSZ", "ROG": 27, "CO": 63, "NOx": 647, "PM10": 60.2, "PM2_5": 0, "DPM": 60.2, "SOx": 395, "CO2e": 0},
    {"Year": 2005, "Mode": "Maneuver", "ROG": 53, "CO": 58, "NOx": 458, "PM10": 43.6, "PM2_5": 0, "DPM": 43.6, "SOx": 157, "CO2e": 0},
    {"Year": 2005, "Mode": "Berth", "ROG": 21, "CO": 65, "NOx": 767, "PM10": 61.3, "PM2_5": 0, "DPM": 61.3, "SOx": 464, "CO2e": 0},
    {"Year": 2005, "Mode": "Anchorage", "ROG": 1, "CO": 2, "NOx": 24, "PM10": 2.0, "PM2_5": 0, "DPM": 2.0, "SOx": 15, "CO2e": 0},

    {"Year": 2012, "Mode": "Cruise", "ROG": 30, "CO": 42, "NOx": 618, "PM10": 14.0, "PM2_5": 13.0, "DPM": 12.0, "SOx": 65, "CO2e": 24712},
    {"Year": 2012, "Mode": "RSZ", "ROG": 38, "CO": 52, "NOx": 626, "PM10": 15.3, "PM2_5": 14.2, "DPM": 12.7, "SOx": 70, "CO2e": 26598},
    {"Year": 2012, "Mode": "Maneuver", "ROG": 72, "CO": 61, "NOx": 512, "PM10": 13.6, "PM2_5": 12.6, "DPM": 12.4, "SOx": 34, "CO2e": 17551},
    {"Year": 2012, "Mode": "Berth", "ROG": 36, "CO": 75, "NOx": 825, "PM10": 23.7, "PM2_5": 22.0, "DPM": 20.1, "SOx": 119, "CO2e": 64619},
    {"Year": 2012, "Mode": "Anchorage", "ROG": 0, "CO": 1, "NOx": 11, "PM10": 0.3, "PM2_5": 0.3, "DPM": 0.3, "SOx": 2, "CO2e": 853},

    {"Year": 2015, "Mode": "Cruise", "ROG": 25.25, "CO": 36.10, "NOx": 502.00, "PM10": 8.51, "PM2_5": 7.84, "DPM": 8.13, "SOx": 31.00, "CO2e": 21091},
    {"Year": 2015, "Mode": "RSZ", "ROG": 32.06, "CO": 44.52, "NOx": 509.79, "PM10": 9.27, "PM2_5": 8.52, "DPM": 8.66, "SOx": 32.95, "CO2e": 22673},
    {"Year": 2015, "Mode": "Maneuver", "ROG": 61.39, "CO": 52.45, "NOx": 416.07, "PM10": 8.93, "PM2_5": 8.24, "DPM": 8.57, "SOx": 10.18, "CO2e": 15129},
    {"Year": 2015, "Mode": "Berth", "ROG": 41.31, "CO": 86.26, "NOx": 890.16, "PM10": 22.61, "PM2_5": 21.05, "DPM": 18.05, "SOx": 48.72, "CO2e": 82067},
    {"Year": 2015, "Mode": "Anchorage", "ROG": 17.19, "CO": 36.13, "NOx": 369.51, "PM10": 8.86, "PM2_5": 8.15, "DPM": 7.88, "SOx": 17.93, "CO2e": 28792},

    {"Year": 2017, "Mode": "Cruise", "ROG": 31.17, "CO": 44.49, "NOx": 651.45, "PM10": 11.37, "PM2_5": 10.53, "DPM": 10.01, "SOx": 41.25, "CO2e": 26040},
    {"Year": 2017, "Mode": "RSZ", "ROG": 39.11, "CO": 52.83, "NOx": 592.27, "PM10": 11.78, "PM2_5": 10.93, "DPM": 10.05, "SOx": 42.46, "CO2e": 25046},
    {"Year": 2017, "Mode": "Maneuver", "ROG": 74.75, "CO": 64.47, "NOx": 526.35, "PM10": 11.47, "PM2_5": 10.60, "DPM": 10.60, "SOx": 13.14, "CO2e": 18938},
    {"Year": 2017, "Mode": "Berth", "ROG": 20.83, "CO": 43.33, "NOx": 444.05, "PM10": 11.80, "PM2_5": 11.02, "DPM": 8.84, "SOx": 27.02, "CO2e": 45240},
    {"Year": 2017, "Mode": "Anchorage", "ROG": 3.70, "CO": 7.76, "NOx": 78.44, "PM10": 1.96, "PM2_5": 1.82, "DPM": 1.66, "SOx": 3.96, "CO2e": 6714},

    {"Year": 2020, "Mode": "Cruise", "ROG": 25.22, "CO": 44.75, "NOx": 491.62, "PM10": 6.23, "PM2_5": 5.73, "DPM": 6.16, "SOx": 12.10, "CO2e": 19560},
    {"Year": 2020, "Mode": "RSZ", "ROG": 31.30, "CO": 51.83, "NOx": 455.96, "PM10": 6.56, "PM2_5": 6.04, "DPM": 6.17, "SOx": 12.09, "CO2e": 19545},
    {"Year": 2020, "Mode": "Maneuver", "ROG": 60.58, "CO": 60.67, "NOx": 415.25, "PM10": 6.70, "PM2_5": 6.17, "DPM": 6.40, "SOx": 9.32, "CO2e": 15057},
    {"Year": 2020, "Mode": "Berth", "ROG": 18.38, "CO": 38.99, "NOx": 378.99, "PM10": 9.23, "PM2_5": 8.49, "DPM": 5.63, "SOx": 25.34, "CO2e": 42492},
    {"Year": 2020, "Mode": "Anchorage", "ROG": 8.45, "CO": 17.75, "NOx": 179.71, "PM10": 3.44, "PM2_5": 3.16, "DPM": 2.81, "SOx": 8.79, "CO2e": 14200},
]

df = pd.DataFrame(data)
df_activity = pd.DataFrame(activity_data)
df_ogv_modes = pd.DataFrame(ogv_modes)

truck_modes = [
    {"Year": 2012, "Mode": "Surface Roads", "ROG": 3.14, "CO": 11.19, "NOx": 80.0, "PM10": 1.76, "PM2_5": 1.21, "DPM": 1.02, "SOx": 0.127, "CO2e": 14994},
    {"Year": 2012, "Mode": "Gate Idling", "ROG": 1.76, "CO": 9.48, "NOx": 15.5, "PM10": 0.12, "PM2_5": 0.11, "DPM": 0.12, "SOx": 0.015, "CO2e": 1562},
    {"Year": 2012, "Mode": "In-Terminal Idling", "ROG": 3.38, "CO": 18.15, "NOx": 29.8, "PM10": 0.23, "PM2_5": 0.22, "DPM": 0.23, "SOx": 0.028, "CO2e": 2989},
    {"Year": 2012, "Mode": "In-Terminal Driving", "ROG": 4.32, "CO": 9.86, "NOx": 9.9, "PM10": 0.88, "PM2_5": 0.65, "DPM": 0.60, "SOx": 0.049, "CO2e": 8654},

    {"Year": 2015, "Mode": "Surface Roads", "ROG": 2.21, "CO": 7.02, "NOx": 46.93, "PM10": 0.83, "PM2_5": 0.43, "DPM": 0.22, "SOx": 0.11, "CO2e": 12385},
    {"Year": 2015, "Mode": "Gate Idling", "ROG": 0.42, "CO": 1.68, "NOx": 11.61, "PM10": 0.002, "PM2_5": 0.002, "DPM": 0.002, "SOx": 0.02, "CO2e": 1838},
    {"Year": 2015, "Mode": "In-Terminal Idling", "ROG": 0.71, "CO": 2.84, "NOx": 19.66, "PM10": 0.004, "PM2_5": 0.004, "DPM": 0.004, "SOx": 0.03, "CO2e": 3113},
    {"Year": 2015, "Mode": "In-Terminal Driving", "ROG": 2.68, "CO": 8.45, "NOx": 35.85, "PM10": 0.40, "PM2_5": 0.23, "DPM": 0.13, "SOx": 0.05, "CO2e": 7619},

    {"Year": 2017, "Mode": "Surface Roads", "ROG": 1.07, "CO": 3.35, "NOx": 23.15, "PM10": 0.488, "PM2_5": 0.251, "DPM": 0.125, "SOx": 0.07, "CO2e": 7276},
    {"Year": 2017, "Mode": "Gate Idling", "ROG": 0.43, "CO": 4.10, "NOx": 8.31, "PM10": 0.003, "PM2_5": 0.003, "DPM": 0.003, "SOx": 0.01, "CO2e": 1272},
    {"Year": 2017, "Mode": "In-Terminal Idling", "ROG": 0.99, "CO": 9.50, "NOx": 19.27, "PM10": 0.007, "PM2_5": 0.006, "DPM": 0.007, "SOx": 0.03, "CO2e": 2947},
    {"Year": 2017, "Mode": "In-Terminal Driving", "ROG": 2.19, "CO": 6.96, "NOx": 29.17, "PM10": 0.404, "PM2_5": 0.222, "DPM": 0.127, "SOx": 0.07, "CO2e": 8310},

    {"Year": 2020, "Mode": "Surface Roads", "ROG": 0.97, "CO": 3.22, "NOx": 25.30, "PM10": 0.937, "PM2_5": 0.373, "DPM": 0.104, "SOx": 0.09, "CO2e": 9945},
    {"Year": 2020, "Mode": "Gate Idling", "ROG": 0.59, "CO": 6.34, "NOx": 10.19, "PM10": 0.003, "PM2_5": 0.003, "DPM": 0.003, "SOx": 0.02, "CO2e": 1735},
    {"Year": 2020, "Mode": "In-Terminal Idling", "ROG": 1.32, "CO": 14.22, "NOx": 22.83, "PM10": 0.008, "PM2_5": 0.007, "DPM": 0.008, "SOx": 0.04, "CO2e": 3890},
    {"Year": 2020, "Mode": "In-Terminal Driving", "ROG": 1.85, "CO": 6.26, "NOx": 30.95, "PM10": 0.749, "PM2_5": 0.307, "DPM": 0.094, "SOx": 0.09, "CO2e": 10211},
]
df_truck_modes = pd.DataFrame(truck_modes)

os.makedirs("data", exist_ok=True)
df.to_csv("data/oakland_emissions_master.csv", index=False)
df_activity.to_csv("data/activity_metrics.csv", index=False)
df_ogv_modes.to_csv("data/ogv_modes.csv", index=False)
df_truck_modes.to_csv("data/truck_modes.csv", index=False)

print("Master dataset saved to data/oakland_emissions_master.csv")
print("Activity metrics saved to data/activity_metrics.csv")
print("OGV Modes saved to data/ogv_modes.csv")
print("Truck Modes saved to data/truck_modes.csv")