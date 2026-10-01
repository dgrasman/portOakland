import sqlite3
import os
from datetime import datetime

DB_PATH = "data/port_traffic.db"

def init_db():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table to track every time a ship changes status (Arrivals, Departures, Anchoring)
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
    conn.commit()
    conn.close()

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
