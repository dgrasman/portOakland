import os
import sqlite3
import sys
import time
import requests
from dotenv import load_dotenv

from db_manager import DB_PATH, length_archetype, now_utc

load_dotenv()

API_BASE = "https://api.vesselapi.com/v1"
API_KEY = os.getenv("VESSEL_MMSI_API_KEY", "").strip().strip("'\"")


def fetch_vessel(mmsi):
    """Fetches static vessel data from VesselAPI. Returns (vessel_dict, remaining_quota, error_message)."""
    if not API_KEY:
        return None, None, "VESSEL_MMSI_API_KEY not found"
    try:
        resp = requests.get(
            f"{API_BASE}/vessel/{mmsi}",
            params={"filter.idType": "mmsi"},
            headers={"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"},
            timeout=10,
        )
        raw_quota = resp.headers.get("X-Ratelimit-Remaining", "")
        remaining = int(raw_quota) if raw_quota.isdigit() else None

        if resp.status_code == 404:
            return None, remaining, "Not Found (404)"
        if resp.status_code == 429:
            return None, 0, "Rate Limit / Quota Exceeded (429)"
        resp.raise_for_status()
        return resp.json().get("vessel", {}), remaining, None
    except Exception as e:
        return None, None, str(e)


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


NON_CONTAINER_TYPES = ("tanker", "bulk", "vehicle", "car carrier", "tug", "barge", "cement", "wood")

# Container ship GT-to-TEU divisors by minimum Gross Tonnage
GT_PER_TEU = [(120000, 9.6), (80000, 9.9), (40000, 10.5), (0, 11.2)]

# Container ships by TEU: (min TEU, installed aux kW, at-berth load kW)
CONTAINER_AUX_KW = [
    (14000, 16500, 2200),
    (10000, 14000, 1900),
    (7000, 11500, 1600),
    (4000, 8500, 1300),
    (2000, 6000, 1000),
    (0, 4500, 750),
]


def compute_refined_teu(api_teu, gt, length, vessel_type, classification):
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

    is_container = "container" in vtype or (
        not any(k in vtype for k in NON_CONTAINER_TYPES)
        and (("cargo" in vtype and (gt or 0) >= 30000) or (classification == "Cargo / Freight" and not vtype and (length or 0) >= 180))
    )
    if not is_container:
        return 0, "Non-Container Vessel"

    if gt and gt > 0:
        divisor = next(div for min_gt, div in GT_PER_TEU if gt >= min_gt)
        return int(round(gt / divisor)), "GT Regression Model"

    if length and length > 0:
        teu, _, label = length_archetype(length)
        return teu, f"Length Archetype ({label})"

    return 0, "Unknown"


def compute_auxiliary_specs(teu, gt, vessel_type, classification):
    """
    Returns (installed_aux_kw, at_berth_load_kw) following CARB OGV inventory methodology.
    The at-berth load is the average hotel + reefer electrical demand.
    """
    vtype = (vessel_type or "").lower()

    if (teu and teu > 0) or "container" in vtype:
        size = teu or (round(gt / 10.0) if gt else 4000)
        return next((inst, berth) for min_teu, inst, berth in CONTAINER_AUX_KW if size >= min_teu)

    if "tanker" in vtype or classification == "Tanker":
        tonnage = gt or 30000
        return (5500, 1800) if tonnage >= 60000 else (4000, 1500) if tonnage >= 30000 else (2800, 1100)

    if any(k in vtype for k in ("vehicle", "car carrier", "ro-ro", "roro")):
        return 4500, 950
    if "bulk" in vtype:
        return 2400, 420
    return (4500, 800) if (gt or 20000) >= 40000 else (2500, 500)


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
        if row["last_api_update"]:
            return True, f"MMSI {mmsi} already enriched on {row['last_api_update']}", None

        api_vessel, remaining, err = fetch_vessel(mmsi)
        if err:
            if "404" in err:
                conn.execute("""
                    UPDATE vessel_particulars
                    SET teu_source = COALESCE(teu_source, 'Not in VesselAPI registry'), last_api_update = ?
                    WHERE mmsi = ? AND last_api_update IS NULL
                """, (now_utc(), str(mmsi)))
            return False, f"API error for {mmsi}: {err}", remaining

        record = build_enriched_record(mmsi, dict(row), api_vessel)
        assignments = ", ".join(f"{col} = :{col}" for col in record if col != "mmsi")
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
    query = f"""
        SELECT mmsi, ship_name FROM vessel_particulars
        WHERE is_oakland_berth = 1 AND last_api_update IS NULL
        ORDER BY oakland_berth_count DESC, length DESC
        {f'LIMIT {int(limit)}' if limit else ''}
    """
    with sqlite3.connect(db_path) as conn:
        candidates = conn.execute(query).fetchall()

    total = len(candidates)
    print(f"\n[ENRICHMENT] Starting batch enrichment for {total} vessels (Safety Reserve: {safety_reserve})")

    enriched = not_found = errors = 0
    remaining = None

    for index, (mmsi, name) in enumerate(candidates, 1):
        if remaining is not None and remaining <= safety_reserve:
            print(f"[QUOTA ALERT] Stopping early: {remaining} requests left (reserve is {safety_reserve}).")
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
                break

        time.sleep(delay)

    print(f"\n[COMPLETED] Enriched: {enriched} | 404 Not Found: {not_found} | Errors: {errors} | Final Quota Remaining: {remaining}\n")


if __name__ == "__main__":
    enrich_all_vessels(limit=int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 20)
