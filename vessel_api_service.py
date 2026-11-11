import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request

from dotenv import load_dotenv

from db_manager import DB_PATH, length_archetype, now_utc

load_dotenv()

API_BASE = "https://api.vesselapi.com/v1"


def get_api_key():
    return os.getenv("VESSEL_MMSI_API_KEY", "").strip().strip("'\"") or None


def api_get(path, timeout=10):
    """
    GET a VesselAPI endpoint.
    Returns (json_data, remaining_monthly_quota, error_message).
    """
    key = get_api_key()
    if not key:
        return None, None, "VESSEL_MMSI_API_KEY not found"

    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "User-Agent": "PortOakland-Enrichment/1.0",
    }
    try:
        with urllib.request.urlopen(urllib.request.Request(API_BASE + path, headers=headers), timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), _remaining_quota(resp.headers), None
    except urllib.error.HTTPError as e:
        remaining = _remaining_quota(e.headers)
        if e.code == 404:
            return None, remaining, "Not Found (404)"
        if e.code == 429:
            return None, 0, "Rate Limit / Quota Exceeded (429)"
        return None, remaining, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return None, None, str(e)


def _remaining_quota(headers):
    raw = headers.get("X-Ratelimit-Remaining")
    return int(raw) if raw and raw.isdigit() else None


def fetch_vessel(mmsi):
    """Static vessel data. Returns (vessel_dict, remaining_quota, error_message)."""
    data, remaining, err = api_get(f"/vessel/{mmsi}?filter.idType=mmsi")
    return (None if err else data.get("vessel", {})), remaining, err

# --------------------------------------------------------------------------
# Fuel capability
# --------------------------------------------------------------------------

# Engine-model tags (MAN B&W, WinGD, Wärtsilä, Bergen) -> (fuel_type, fuel_capability). First match wins.
FUEL_RULES = [
    (["-GI", "ME-GA", "-DF", "XDF", " DUAL FUEL", "50DF", "46DF", "34DF", "20DF"], "LNG / MGO", "LNG Dual-Fuel (Gas + MGO Pilot)"),
    (["LGIM", "METHANOL"], "Methanol / MGO", "Methanol Dual-Fuel (Methanol + MGO Pilot)"),
    (["LGIP"], "LPG / MGO", "LPG Dual-Fuel"),
    (["LGIA", "AMMONIA"], "Ammonia / MGO", "Ammonia Dual-Fuel"),
]


def analyze_engine_and_fuel(engine_model, vessel_type):
    """Returns (is_dual_fuel, fuel_type, fuel_capability) from engine model and vessel type."""
    model = (engine_model or "").strip().upper()
    for tags, fuel_type, capability in FUEL_RULES:
        if any(tag in model for tag in tags):
            return 1, fuel_type, capability

    if "LNG" in (vessel_type or "").upper():
        return 1, "LNG / MGO", "LNG Dual-Fuel"
    return 0, "VLSFO / MGO", "Conventional Marine Fuel (MGO / VLSFO)"

# --------------------------------------------------------------------------
# TEU and auxiliary engine estimates
# --------------------------------------------------------------------------

NON_CONTAINER_TYPES = ["tanker", "bulk", "vehicle", "car carrier", "tug", "barge", "cement", "wood"]


def compute_refined_teu(api_teu, gross_tonnage, length, vessel_type, classification):
    """
    Returns (teu, source), trying in order:
    1. TEU reported by VesselAPI
    2. 0 for non-container vessels (tankers, bulkers, car carriers, ...)
    3. Regression on gross tonnage for container ships
    4. CARB length archetype
    """
    vtype = (vessel_type or "").lower()

    if api_teu and api_teu > 0:
        return int(api_teu), "VesselAPI Verified"

    if "container" not in vtype and any(kind in vtype for kind in NON_CONTAINER_TYPES):
        return 0, "Non-Container Vessel"

    is_container = (
        "container" in vtype
        or ("cargo" in vtype and gross_tonnage and gross_tonnage >= 30000)
        or (classification == "Cargo / Freight" and not vtype and length and length >= 180)
    )
    if not is_container:
        return 0, "Non-Container Vessel"

    if gross_tonnage and gross_tonnage > 0:
        if gross_tonnage >= 120000:
            gt_per_teu = 9.6
        elif gross_tonnage >= 80000:
            gt_per_teu = 9.9
        elif gross_tonnage >= 40000:
            gt_per_teu = 10.5
        else:
            gt_per_teu = 11.2
        return int(round(gross_tonnage / gt_per_teu)), "GT Regression Model"

    if length and length > 0:
        teu, _, label = length_archetype(length)
        return teu, f"Length Archetype ({label})"

    return 0, "Unknown"


# Container ships by TEU: (min TEU, installed aux kW, at-berth load kW)
CONTAINER_AUX_KW = [
    (14000, 16500, 2200),
    (10000, 14000, 1900),
    (7000, 11500, 1600),
    (4000, 8500, 1300),
    (2000, 6000, 1000),
    (0, 4500, 750),
]


def compute_auxiliary_specs(teu, gross_tonnage, vessel_type, classification):
    """
    Returns (installed_aux_kw, at_berth_load_kw) following CARB OGV inventory methodology.
    The at-berth load is the average hotel + reefer electrical demand.
    """
    vtype = (vessel_type or "").lower()

    if (teu and teu > 0) or "container" in vtype:
        size = teu or (round(gross_tonnage / 10.0) if gross_tonnage else 4000)
        for min_teu, installed_kw, berth_kw in CONTAINER_AUX_KW:
            if size >= min_teu:
                return installed_kw, berth_kw

    if "tanker" in vtype or classification == "Tanker":
        gt = gross_tonnage or 30000
        if gt >= 60000:
            return 5500, 1800
        if gt >= 30000:
            return 4000, 1500
        return 2800, 1100

    if any(kind in vtype for kind in ["vehicle", "car carrier", "ro-ro", "roro"]):
        return 4500, 950

    if "bulk" in vtype:
        return 2400, 420

    # General cargo / other
    if (gross_tonnage or 20000) >= 40000:
        return 4500, 800
    return 2500, 500

# --------------------------------------------------------------------------
# Enrichment
# --------------------------------------------------------------------------

def build_enriched_record(mmsi, ais_row, api_vessel):
    """Combines the AIS row from the database with the VesselAPI payload into one record."""
    gt = api_vessel.get("gross_tonnage")
    vessel_type = api_vessel.get("vessel_type") or ""
    classification = ais_row.get("classification") or "Cargo / Freight"
    length = api_vessel.get("length") or ais_row.get("length")

    teu, teu_source = compute_refined_teu(api_vessel.get("teu"), gt, length, vessel_type, classification)
    aux_installed_kw, aux_berth_kw = compute_auxiliary_specs(teu, gt, vessel_type, classification)
    is_dual_fuel, fuel_type, fuel_capability = analyze_engine_and_fuel(api_vessel.get("engine_model_name"), vessel_type)

    return {
        "mmsi": str(mmsi),
        "imo": api_vessel.get("imo"),
        "ship_name": (api_vessel.get("name") or ais_row.get("ship_name") or "Unknown").strip(),
        "vessel_type": vessel_type,
        "vessel_subtype": api_vessel.get("vessel_subtype") or "",
        "length": length,
        "width": api_vessel.get("breadth") or ais_row.get("width"),
        "gross_tonnage": gt,
        "GT": gt,
        "gt_source": "VesselAPI Verified" if gt else None,
        "deadweight_tonnage": api_vessel.get("deadweight_tonnage"),
        "teu_capacity": teu,
        "teu_source": teu_source,
        "main_engine_kw": api_vessel.get("kilowatt_power"),
        "engine_model": api_vessel.get("engine_model_name"),
        "engine_type": api_vessel.get("engine_type"),
        "aux_engine_capacity_kw": aux_installed_kw,
        "aux_engine_kw": aux_berth_kw,  # at-berth operating load
        "fuel_type": fuel_type,
        "is_dual_fuel": is_dual_fuel,
        "fuel_capability": fuel_capability,
        "flag_country": api_vessel.get("country"),
        "year_built": api_vessel.get("year_built"),
        "call_sign": api_vessel.get("call_sign"),
        "last_api_update": now_utc(),
    }


def enrich_vessel_in_db(mmsi, db_path=DB_PATH):
    """
    Fetches one vessel from VesselAPI and saves it to vessel_particulars.
    Skips vessels that were already enriched, and stamps 404s so later runs don't re-query them.
    Returns (success, message, remaining_quota).
    """
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM vessel_particulars WHERE mmsi = ?", (str(mmsi),)).fetchone()
        if not row:
            return False, f"MMSI {mmsi} not found in vessel_particulars", None
        ais_row = dict(row)
        if ais_row["last_api_update"]:
            return True, f"MMSI {mmsi} already enriched on {ais_row['last_api_update']}", None

        api_vessel, remaining, err = fetch_vessel(mmsi)
        if err:
            if "404" in err:
                conn.execute("""
                    UPDATE vessel_particulars
                    SET teu_source = COALESCE(teu_source, 'Not in VesselAPI registry'), last_api_update = ?
                    WHERE mmsi = ? AND last_api_update IS NULL
                """, (now_utc(), str(mmsi)))
            return False, f"API error for {mmsi}: {err}", remaining

        record = build_enriched_record(mmsi, ais_row, api_vessel)
        assignments = ", ".join(f"{column} = :{column}" for column in record if column != "mmsi")
        conn.execute(f"UPDATE vessel_particulars SET {assignments} WHERE mmsi = :mmsi", record)

    message = (f"Enriched {record['ship_name']} (IMO: {record['imo']}, GT: {record['gross_tonnage']}, "
               f"TEU: {record['teu_capacity']}, Fuel: {record['fuel_capability']})")
    return True, message, remaining


def enrich_all_vessels(limit=25, safety_reserve=5, delay=0.15, db_path=DB_PATH):
    """
    Enriches vessels that have berthed at the Port of Oakland and aren't enriched yet,
    most frequent callers (then longest) first.
    Stops early when the remaining monthly quota drops to safety_reserve, or on HTTP 429.
    """
    if not get_api_key():
        print("[ERROR] VESSEL_MMSI_API_KEY is missing from environment or .env")
        return {"success": False, "error": "Missing API key"}

    query = """
        SELECT mmsi, ship_name FROM vessel_particulars
        WHERE is_oakland_berth = 1 AND last_api_update IS NULL
        ORDER BY oakland_berth_count DESC, length DESC
    """
    if limit:
        query += f" LIMIT {int(limit)}"

    with sqlite3.connect(db_path) as conn:
        candidates = conn.execute(query).fetchall()

    total = len(candidates)
    print(f"\n[ENRICHMENT] Starting batch enrichment for {total} vessels (Safety Reserve: {safety_reserve})")

    enriched = not_found = errors = 0
    remaining = None

    for index, (mmsi, name) in enumerate(candidates, 1):
        if remaining is not None and remaining <= safety_reserve:
            print(f"[QUOTA ALERT] Stopping enrichment early: only {remaining} requests remaining this billing cycle (safety reserve is {safety_reserve}).")
            break

        success, message, remaining = enrich_vessel_in_db(mmsi, db_path=db_path)

        if success:
            enriched += 1
            quota = f" [Quota Left: {remaining}]" if remaining is not None else ""
            print(f"[{index}/{total}] SUCCESS: {message}{quota}")
        elif "404" in message:
            not_found += 1
            print(f"[{index}/{total}] 404 NOT FOUND: {name} (MMSI: {mmsi})")
        else:
            errors += 1
            print(f"[{index}/{total}] ERROR: {name} (MMSI: {mmsi}) - {message}")
            if "429" in message:
                print("[QUOTA EXHAUSTED] Halting due to HTTP 429 quota exhaustion.")
                break

        time.sleep(delay)

    print(f"\n[COMPLETED] Enriched: {enriched} | 404 Not Found: {not_found} | Errors: {errors} | Final Quota Remaining: {remaining}\n")
    return {
        "success": True,
        "enriched": enriched,
        "not_found": not_found,
        "errors": errors,
        "remaining_quota": remaining,
    }


if __name__ == "__main__":
    enrich_all_vessels(limit=int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20)
