import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from db_manager import init_db, log_event_to_db

# Load variables from the .env file
load_dotenv()

# API KEY
API_KEY = os.getenv("AISSTREAM_API_KEY")

# Dictionary to store data (Position and Destination in separate messages)
live_ships = {}

async def listen_to_ais_stream():
    if not API_KEY or API_KEY == "your_aisstream_api_key_here":
        print("API Key error")
        return

    # Initialize the database
    init_db()
    print("Database initialized.")

    # wss:// means WebSocket Secure (encrypted)
    uri = "wss://stream.aisstream.io/v0/stream"
    
    while True:
        try:
            print(f"Connecting to secure WebSocket at {uri}...")
            # Establish the connection
            async with websockets.connect(uri) as websocket:
                print("Connected successful. Sending subscription request...")
                
                # Bounding box for Oakland, San Francisco, and the offshore anchorages
                sf_bay_bounding_box = [[[37.70, -122.55], [37.85, -122.25]]]
                
                subscribe_message = {
                    "APIKey": API_KEY,
                    "BoundingBoxes": sf_bay_bounding_box,
                    # PositionReports and ShipStaticData (contains the Destination)
                    "FilterMessageTypes": ["PositionReport", "ShipStaticData"] 
                }
                
                # Subscription as JSON string
                await websocket.send(json.dumps(subscribe_message))
                print("Subscribed to San Francisco Bay traffic. Waiting for ships...\n")
                
                # Listen indefinitely for incoming messages
                async for message_json in websocket:
                    message = json.loads(message_json)
                    msg_type = message.get("MessageType")
                    meta = message.get("MetaData", {})
                    mmsi = meta.get("MMSI", "Unknown")
                    
                    # Initialize the ship if we haven't seen it yet
                    if mmsi not in live_ships:
                        live_ships[mmsi] = {
                            "Name": meta.get("ShipName", "Unknown").strip(), 
                            "Destination": "Unknown",
                            "LastStatus": "Unknown",
                            "LastLocation": "Unknown"
                        }

                    # Update Destination if we receive Static Data
                    if msg_type == "ShipStaticData":
                        static_data = message.get("Message", {}).get("ShipStaticData", {})
                        destination = static_data.get("Destination", "Unknown").strip().upper()
                        if destination:
                            live_ships[mmsi]["Destination"] = destination

                    # Update Location and Status if position report received
                    if msg_type == "PositionReport":
                        report = message.get("Message", {}).get("PositionReport", {})
                        nav_status = report.get("NavigationalStatus", "Unknown")
                        speed = report.get("Sog", 0) # Speed Over Ground
                        lat = meta.get("latitude", 0)
                        lon = meta.get("longitude", 0)
                        
                        dest = live_ships[mmsi]["Destination"]
                        ship_name = live_ships[mmsi]["Name"]
                        
                        # Determine where the ship is physically located
                        physical_location = "SF Bay / Ocean"
                        if lon > -122.35 and lat > 37.78:
                            physical_location = "Port of Oakland"
                        elif lon < -122.38 and lat < 37.82:
                            physical_location = "Port of San Francisco"

                        # Determine ship activity
                        status_text = "Moving"
                        if nav_status == 1:
                            status_text = f"At Anchor"
                            # Flag if anchored but waiting for Oakland
                            if "OAK" in dest:
                                status_text = "At Anchor (Waiting for Oakland)"
                        elif nav_status == 5:
                            status_text = f"Moored"
                            
                        # CRITICAL LOGIC: Only save to DB if the status or location has CHANGED
                        current_state = f"{status_text} | {physical_location}"
                        previous_state = f"{live_ships[mmsi]['LastStatus']} | {live_ships[mmsi]['LastLocation']}"
                        
                        if current_state != previous_state:
                            # Log the event (e.g. ship just arrived at Oakland berth, or just departed)
                            log_event_to_db(mmsi, ship_name, dest, status_text, physical_location, speed)
                            
                            # Update memory
                            live_ships[mmsi]['LastStatus'] = status_text
                            live_ships[mmsi]['LastLocation'] = physical_location

        except (websockets.exceptions.ConnectionClosed, Exception) as e:
            print(f"Connection dropped ({e}). Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    # Run the asynchronous function
    try:
        asyncio.run(listen_to_ais_stream())
    except KeyboardInterrupt:
        print("\nStopped listening.")
