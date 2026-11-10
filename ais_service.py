import asyncio
import json
import os

import websockets
from dotenv import load_dotenv

from db_manager import init_db, log_event_to_db, upsert_vessel_particulars
from vessel_api_service import enrich_vessel_in_db

load_dotenv()

API_KEY = os.getenv("AISSTREAM_API_KEY")
STREAM_URI = "wss://stream.aisstream.io/v0/stream"  # wss:// = encrypted WebSocket

# Oakland, San Francisco and the offshore anchorages
SF_BAY_BOUNDING_BOX = [[[37.70, -122.55], [37.85, -122.25]]]

# Position and static data (destination, ship type) arrive in separate messages,
# so we remember what we know about each ship, keyed by MMSI.
live_ships = {}


def get_physical_location(lat, lon):
    if lon > -122.35 and lat > 37.78:
        return "Port of Oakland"
    if lon < -122.38 and lat < 37.82:
        return "Port of San Francisco"
    return "SF Bay / Ocean"


def get_status_text(nav_status, destination):
    """Converts an AIS navigational status code into the label we log."""
    if nav_status == 1:
        return "At Anchor (Waiting for Oakland)" if "OAK" in destination else "At Anchor"
    if nav_status == 5:
        return "Moored"
    return "Moving"


def handle_static_data(mmsi, message):
    """Records destination, ship type and size. Only Cargo / Tanker ships are flagged as commercial."""
    ship = live_ships[mmsi]
    static_data = message.get("Message", {}).get("ShipStaticData", {})

    destination = static_data.get("Destination", "Unknown").strip().upper()
    if destination:
        ship["Destination"] = destination

    dimension = static_data.get("Dimension", {})
    length = dimension.get("A", 0) + dimension.get("B", 0)
    width = dimension.get("C", 0) + dimension.get("D", 0)

    ship["is_commercial"] = upsert_vessel_particulars(
        mmsi, ship["Name"], static_data.get("Type", 0), length, width
    )


def handle_position_report(mmsi, message):
    """Logs an event whenever a commercial ship's status or location changes."""
    ship = live_ships[mmsi]
    if not ship["is_commercial"]:
        return

    report = message.get("Message", {}).get("PositionReport", {})
    meta = message.get("MetaData", {})

    location = get_physical_location(meta.get("latitude", 0), meta.get("longitude", 0))
    status = get_status_text(report.get("NavigationalStatus", "Unknown"), ship["Destination"])

    # Only save when something changed, otherwise we'd log every position ping
    if (status, location) == (ship["LastStatus"], ship["LastLocation"]):
        return

    log_event_to_db(mmsi, ship["Name"], ship["Destination"], status, location, report.get("Sog", 0))

    # VesselAPI quota is limited, so only look up ships that actually berth at Oakland
    if location == "Port of Oakland" and status == "Moored":
        asyncio.create_task(asyncio.to_thread(enrich_vessel_in_db, mmsi))

    ship["LastStatus"] = status
    ship["LastLocation"] = location


async def listen_to_ais_stream():
    if not API_KEY or API_KEY == "your_aisstream_api_key_here":
        print("API Key error")
        return

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
                    message = json.loads(message_json)
                    meta = message.get("MetaData", {})
                    mmsi = meta.get("MMSI", "Unknown")

                    if mmsi not in live_ships:
                        live_ships[mmsi] = {
                            "Name": meta.get("ShipName", "Unknown").strip(),
                            "Destination": "Unknown",
                            "LastStatus": "Unknown",
                            "LastLocation": "Unknown",
                            "is_commercial": False,  # until static data says otherwise
                        }

                    msg_type = message.get("MessageType")
                    if msg_type == "ShipStaticData":
                        handle_static_data(mmsi, message)
                    elif msg_type == "PositionReport":
                        handle_position_report(mmsi, message)

        except Exception as e:
            print(f"Connection dropped ({e}). Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(listen_to_ais_stream())
    except KeyboardInterrupt:
        print("\nStopped listening.")
