import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = "data/port_traffic.db"

# Every vessel_particulars column except the mmsi key, in display order.
# init_db() creates the table from this list and adds any column an older database is missing.
VESSEL_COLUMNS = {
    "ship_name": "TEXT",
    "classification": "TEXT",
    "GT": "INTEGER",
    "gross_tonnage": "INTEGER",
    "gt_source": "TEXT",
    "is_oakland_berth": "INTEGER DEFAULT 0",
    "oakland_berth_count": "INTEGER DEFAULT 0",
    "teu_capacity": "INTEGER",
    "teu_source": "TEXT",
    "length": "INTEGER",
    "width": "INTEGER",
    "imo": "INTEGER",
    "vessel_type": "TEXT",
    "vessel_subtype": "TEXT",
    "deadweight_tonnage": "INTEGER",
    "ship_type_code": "INTEGER",
    "main_engine_kw": "INTEGER",
    "engine_model": "TEXT",
    "engine_type": "INTEGER",
    "aux_engine_capacity_kw": "INTEGER",
    "aux_engine_kw": "INTEGER",
    "fuel_type": "TEXT",
    "is_dual_fuel": "INTEGER DEFAULT 0",
    "fuel_capability": "TEXT",
    "technical_efficiency": "TEXT",
    "co2_at_berth_annual": "REAL",
    "flag_country": "TEXT",
    "year_built": "INTEGER",
    "call_sign": "TEXT",
    "last_api_update": "DATETIME",
}

# CARB container-ship archetypes by length: (max length in m, TEU, aux load in kW, label)
LENGTH_ARCHETYPES = [
    (200, 1500, 750, "<200m"),
    (260, 4000, 1000, "200-260m"),
    (300, 6500, 1300, "260-300m"),
    (360, 10000, 1600, "300-360m"),
    (float("inf"), 14000, 2000, ">=360m"),
]


def now_utc():
    """Current UTC time as the 'YYYY-MM-DD HH:MM:SS' string stored in the database."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def length_archetype(length):
    """Returns (teu, aux_kw, label) for a vessel length in metres."""
    for max_length, teu, aux_kw, label in LENGTH_ARCHETYPES:
        if length < max_length:
            return teu, aux_kw, label


def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Arrivals / departures
    conn.execute('''
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

    # Vessel specifications & classifications
    conn.execute("CREATE TABLE IF NOT EXISTS vessel_particulars (mmsi TEXT PRIMARY KEY)")
    existing = {row[1] for row in conn.execute("PRAGMA table_info(vessel_particulars)")}
    for name, column_type in VESSEL_COLUMNS.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE vessel_particulars ADD COLUMN {name} {column_type}")

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


def upsert_vessel_particulars(mmsi, name, type_code, length, width):
    """
    Inserts or updates a vessel's static AIS data. Returns True for Cargo / Tanker ships
    (the only ones we track) and False otherwise.
    Existing TEU / aux values are kept (COALESCE) so VesselAPI-enriched data isn't overwritten.
    """
    classification = get_ais_classification(type_code)
    if classification not in ("Cargo / Freight", "Tanker"):
        return False

    # Container-ship estimate from length, until VesselAPI provides real values
    teu = aux_kw = teu_source = None
    if classification == "Cargo / Freight" and length:
        teu, aux_kw, _ = length_archetype(length)
        teu_source = "Length Archetype"

    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO vessel_particulars (
            mmsi, ship_name, ship_type_code, classification, length, width, teu_capacity, aux_engine_kw, teu_source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(mmsi) DO UPDATE SET
            ship_name = excluded.ship_name,
            ship_type_code = excluded.ship_type_code,
            classification = excluded.classification,
            length = CASE WHEN excluded.length > 0 THEN excluded.length ELSE vessel_particulars.length END,
            width = CASE WHEN excluded.width > 0 THEN excluded.width ELSE vessel_particulars.width END,
            teu_capacity = COALESCE(vessel_particulars.teu_capacity, excluded.teu_capacity),
            aux_engine_kw = COALESCE(vessel_particulars.aux_engine_kw, excluded.aux_engine_kw),
            teu_source = COALESCE(vessel_particulars.teu_source, excluded.teu_source)
    ''', (mmsi, name, type_code, classification, length, width, teu, aux_kw, teu_source))
    conn.commit()
    conn.close()
    return True


def log_event_to_db(mmsi, name, dest, status, location, speed):
    """Saves a ship event, and flags the vessel when it moors at the Port of Oakland."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO ship_events (timestamp, mmsi, ship_name, destination, nav_status, physical_location, speed)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (now_utc(), mmsi, name, dest, status, location, speed))

    if location == "Port of Oakland" and status == "Moored":
        conn.execute('''
            UPDATE vessel_particulars
            SET is_oakland_berth = 1,
                oakland_berth_count = COALESCE(oakland_berth_count, 0) + 1
            WHERE mmsi = ?
        ''', (mmsi,))

    conn.commit()
    conn.close()
    print(f"[SAVED TO DB]: {name} is now {status} at {location}")
