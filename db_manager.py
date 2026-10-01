import sqlite3
import os
from datetime import datetime

DB_PATH = "data/port_traffic.db"

def init_db():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Table for tracking Arrivals/Departures
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ship_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            mmsi TEXT,
            ship_name TEXT,
            destination TEXT,
            nav_status TEXT,
            physical_location TEXT,
            speed REAL
        )
    ''')
    
    # 2. Table for Vessel Specifications & Classifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vessel_particulars (
            mmsi TEXT PRIMARY KEY,
            ship_name TEXT,
            ship_type_code INTEGER,
            classification TEXT,
            length INTEGER,
            width INTEGER,
            teu_capacity INTEGER,
            aux_engine_kw INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def get_ais_classification(type_code):
    """Maps standard AIS integer type codes to human-readable vessel classifications."""
    if not type_code:
        return "Unknown"
    if 70 <= type_code <= 79:
        return "Cargo / Freight"
    if 80 <= type_code <= 89:
        return "Tanker"
    if 60 <= type_code <= 69:
        return "Passenger / Cruise"
    if 31 <= type_code <= 32 or type_code == 52:
        return "Tug / Towing"
    if type_code == 30:
        return "Fishing"
    if type_code in (36, 37):
        return "Pleasure Craft / Sailboat"
    
    return f"Other ({type_code})"

def estimate_engine_specs(length, classification):
    """
    Estimates the Auxiliary Engine load (kW) and TEU based on the ship's length 
    using standard CARB OGV archetypes for container ships.
    """
    if classification != "Cargo / Freight" or length == 0:
        return None, None
        
    # Standard length ranges for Container Ships (in meters)
    if length < 200:
        return 1500, 750    # ~1,500 TEU, ~750 kW Aux load
    elif 200 <= length < 260:
        return 4000, 1000   # ~4,000 TEU, ~1,000 kW Aux load
    elif 260 <= length < 300:
        return 6500, 1300   # ~6,500 TEU, ~1,300 kW Aux load
    elif 300 <= length < 360:
        return 10000, 1600  # ~10,000 TEU, ~1,600 kW Aux load
    else:
        return 14000, 2000  # 14,000+ TEU, 2,000+ kW Aux load

def upsert_vessel_particulars(mmsi, name, type_code, length, width):
    """Inserts or updates the vessel's static classification data."""
    classification = get_ais_classification(type_code)
    
    # We really only care about Cargo and Tankers for Port of Oakland emissions
    if classification not in ["Cargo / Freight", "Tanker"]:
        return False
        
    teu, aux_kw = estimate_engine_specs(length, classification)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vessel_particulars (mmsi, ship_name, ship_type_code, classification, length, width, teu_capacity, aux_engine_kw)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mmsi) DO UPDATE SET
            ship_name=excluded.ship_name,
            ship_type_code=excluded.ship_type_code,
            classification=excluded.classification,
            length=excluded.length,
            width=excluded.width,
            teu_capacity=excluded.teu_capacity,
            aux_engine_kw=excluded.aux_engine_kw
    ''', (mmsi, name, type_code, classification, length, width, teu, aux_kw))
    
    conn.commit()
    conn.close()
    return True

def log_event_to_db(mmsi, name, dest, status, location, speed):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO ship_events (timestamp, mmsi, ship_name, destination, nav_status, physical_location, speed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, mmsi, name, dest, status, location, speed))
    
    conn.commit()
    conn.close()
    print(f"[SAVED TO DB]: {name} is now {status} at {location}")
