import asyncio
import json
import os

import websockets
from dotenv import load_dotenv

from db_manager import init_db, log_event_to_db, upsert_vessel_particulars
from vessel_api_service import enrich_vessel_in_db

load_dotenv()

API_KEY = os.getenv("AISSTREAM_API_KEY")
STREAM_URI = "wss://stream.aisstream.io/v0/stream" 

# Boundary Boxes for San Francisco and Oakland Ports
SF_BAY_BOUNDING_BOX = [[[37.70, -122.55], [37.85, -122.25]]]

# open dictionary for ship ASI activity tracking
live_ships = {}

# boundary box determine location of ship
def get_physical_location(lat, lon):
    if lon > -122.35 and lat > 37.78:
        return "Port of Oakland"
    if lon < -122.38 and lat < 37.82:
        return "Port of San Francisco"
    return "SF Bay / Ocean"


def get_status_text(nav_status, destination):
    """Translates AIS navigational status code into log."""
    if nav_status == 1:
        return "At Anchor (Waiting for Oakland)" if "OAK" in destination else "At Anchor"
    return "Moored" if nav_status == 5 else "Moving"


async def listen_to_ais_stream():
    init_db()
    print("Database initialized.")

    while True:
        try:
            print(f"Connecting to secure WebSocket at {STREAM_URI}...")
            async with websockets.connect(STREAM_URI) as websocket:
                await websocket.send(json.dumps({
                    "APIKey": API_KEY,
                    "BoundingBoxes": SF_BAY_BOUNDING_BOX,
                    "FilterMessageTypes": ["PositionReport", "ShipStaticData"],
                }))
                print("Subscribed to San Francisco Bay traffic. Waiting for ships...\n")

                async for message_json in websocket:
                    data = json.loads(message_json)
                    meta = data.get("MetaData", {})
                    msg = data.get("Message", {})
                    mmsi = meta.get("MMSI", "Unknown")
                    name = meta.get("ShipName", "Unknown").strip()
                    ship = live_ships.setdefault(mmsi, {"dest": "Unknown", "commercial": False, "state": None})

                    # record destination, dimensions, and whether the ship is Cargo / Tanker
                    if "ShipStaticData" in msg:
                        static = msg["ShipStaticData"]
                        ship["dest"] = static.get("Destination", "").strip().upper() or ship["dest"]
                        dim = static.get("Dimension", {})
                        ship["commercial"] = upsert_vessel_particulars(
                            mmsi, name, static.get("Type", 0),
                            dim.get("A", 0) + dim.get("B", 0),
                            dim.get("C", 0) + dim.get("D", 0),
                        )

                    # log whenever a commercial ship's status or location changes
                    elif "PositionReport" in msg and ship["commercial"]:
                        report = msg["PositionReport"]
                        state = (
                            get_status_text(report.get("NavigationalStatus"), ship["dest"]),
                            get_physical_location(meta.get("latitude", 0), meta.get("longitude", 0)),
                        )
                        if state != ship["state"]:
                            ship["state"] = state
                            status, location = state
                            log_event_to_db(mmsi, name, ship["dest"], status, location, report.get("Sog", 0))
                            if state == ("Moored", "Port of Oakland"):
                                asyncio.create_task(asyncio.to_thread(enrich_vessel_in_db, mmsi))

        except Exception as e:
            print(f"Connection dropped ({e}). Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(listen_to_ais_stream())
    except KeyboardInterrupt:
        print("\nStopped listening.")
