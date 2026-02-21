#!/usr/bin/env python3
"""
Segelflug-Thermikvorhersage – Multi-Region
Ruft Open-Meteo API (ICON-D2) ab, integriert DHV-Wetter und berechnet Thermik-Scores.
Für OpenClaw als Skill konzipiert.
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError
from math import sqrt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def list_regions(config):
    """Print available regions as JSON for the agent to display."""
    regions = config["regions"]
    out = []
    for rid, r in regions.items():
        out.append({
            "id": rid,
            "name": r["name"],
            "emoji": r.get("emoji", "📍"),
            "description": r.get("description", ""),
            "lat": r["latitude"],
            "lon": r["longitude"],
            "type": r.get("type", "unknown"),
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))


def resolve_region(args, config):
    """Resolve region from args. Returns dict with lat, lon, name, elevation, type, dhv_region."""
    if args.region:
        rid = args.region.lower().replace("-", "_").replace(" ", "_")
        regions = config["regions"]
        if rid not in regions:
            # Try fuzzy match
            for key, val in regions.items():
                if rid in key or rid in val["name"].lower():
                    rid = key
                    break
            else:
                print(json.dumps({
                    "error": f"Region '{args.region}' nicht gefunden.",
                    "available": list(regions.keys()),
                }), file=sys.stdout)
                sys.exit(1)
        r = regions[rid]
        return {
            "id": rid,
            "name": r["name"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "elevation_m": r.get("elevation_m", 500),
            "type": r.get("type", "alpine"),
            "dhv_region": r.get("dhv_region", "Deutschland"),
        }
    elif args.lat is not None and args.lon is not None:
        name = args.name or f"Custom ({args.lat:.2f}°N, {args.lon:.2f}°E)"
        rtype = args.type or "alpine"
        return {
            "id": "custom",
            "name": name,
            "latitude": args.lat,
            "longitude": args.lon,
            "elevation_m": args.elevation or 500,
            "type": rtype,
            "dhv_region": args.dhv_region or "Deutschland",
        }
    else:
        # Default: first region in config
        first_id = list(config["regions"].keys())[0]
        r = config["regions"][first_id]
        return {
            "id": first_id,
            "name": r["name"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "elevation_m": r.get("elevation_m", 500),
            "type": r.get("type", "alpine"),
            "dhv_region": r.get("dhv_region", "Deutschland"),
        }


# ---------------------------------------------------------------------------
# Open-Meteo API
# ---------------------------------------------------------------------------

def fetch_open_meteo(lat, lon, days, model="icon_d2"):
    """Fetch all thermal-relevant parameters from Open-Meteo API."""
    hourly_params = [
        "temperature_2m", "dew_point_2m", "relative_humidity_2m",
        "precipitation", "rain",
        "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
        "wind_speed_10m", "wind_speed_80m",
        "wind_direction_10m", "wind_direction_80m",
        "wind_gusts_10m",
        "cape", "lifted_index", "convective_inhibition",
        "boundary_layer_height",
        "shortwave_radiation", "direct_radiation",
        "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm", "soil_temperature_0cm",
    ]
    params_str = ",".join(hourly_params)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={params_str}"
        f"&models={model}"
        f"&forecast_days={days}"
        f"&timezone=Europe%2FBerlin"
        f"&wind_speed_unit=kmh"
    )
    try:
        req = Request(url, headers={"User-Agent": "SoaringWeather/2.0"})
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return data
    except URLError as e:
        if model != "icon_eu":
            print(f"[WARN] {model} failed ({e}), trying icon_eu...", file=sys.stderr)
            return fetch_open_meteo(lat, lon, days, model="icon_eu")
        raise


# ---------------------------------------------------------------------------
# DHV Integration
# ---------------------------------------------------------------------------

def fetch_dhv_data(dhv_region="Nordalpen"):
    """Try to fetch DHV weather. Returns dict or None on failure."""
    try:
        dhv_script = os.path.join(SCRIPT_DIR, "fetch_dhv.py")
        if not os.path.exists(dhv_script):
            return None
        # Import dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_dhv", dhv_script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.fetch_and_classify(region_filter=dhv_region)
    except Exception as e:
        print(f"[WARN] DHV fetch failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def safe_val(val, default=0):
    return default if val is None else val


def wind_direction_name(deg):
    if deg is None:
        return "?"
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(deg / 22.5) % 16]


def score_param(value, thresholds, invert=False):
    """Score a parameter 0–3 based on threshold ranges."""
    levels = ["poor", "ok", "good", "very_good", "excellent"]
    scores = [0, 0.75, 1.5, 2.25, 3.0]
    for i, level in enumerate(levels):
        if level in thresholds:
            lo, hi = thresholds[level]
            if lo <= value < hi:
                return scores[i]
    if not invert:
        exc = thresholds.get("excellent", [0, 0])
        return 3.0 if value >= exc[1] else 0
    else:
        exc = thresholds.get("excellent", [0, 0])
        if value < exc[0]:
            return 3.0
        return 0


def estimate_climb_rate(cape, blh, cloud_cover_low, wind_10m):
    """Estimate thermal climb rate in m/s."""
    if cape <= 0 or blh < 300:
        return 0.0
    w_cape = sqrt(2 * safe_val(cape, 0)) * 0.04
    blh_factor = min(safe_val(blh, 0) / 2000, 1.5)
    cc_factor = max(0.3, 1.0 - safe_val(cloud_cover_low, 50) / 150)
    wind_factor = max(0.3, 1.0 - max(0, safe_val(wind_10m, 0) - 15) / 40)
    climb = w_cape * blh_factor * cc_factor * wind_factor
    return round(max(0, min(climb, 5.0)), 1)


def estimate_cloud_base_msl(temp_2m, dewpoint_2m, elevation_m):
    """Estimate cloud base MSL from T-Td spread (125m per °C)."""
    if temp_2m is None or dewpoint_2m is None:
        return None
    spread = temp_2m - dewpoint_2m
    return round(elevation_m + spread * 125)


# ---------------------------------------------------------------------------
# Day analysis
# ---------------------------------------------------------------------------

def analyze_day(hourly, day_idx, config, location):
    """Analyze one day's thermal conditions."""
    scoring = config["scoring"]
    thresholds = scoring["thresholds"]
    weights = scoring["weights"]
    phases_config = scoring["phases"]
    elevation = location["elevation_m"]
    region_type = location.get("type", "alpine")

    start_h = day_idx * 24

    def get_val(param, h):
        arr = hourly.get(param, [])
        idx = start_h + h
        return arr[idx] if idx < len(arr) else None

    times = hourly["time"][start_h:start_h + 24]
    date_str = times[0][:10] if times else "?"
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_de = ["Montag","Dienstag","Mittwoch","Donnerstag",
                      "Freitag","Samstag","Sonntag"][date_obj.weekday()]
    except Exception:
        weekday_de = "?"

    # Core thermal hours 10–17
    core = range(10, 18)
    core_cape = [safe_val(get_val("cape", h)) for h in core]
    core_blh = [safe_val(get_val("boundary_layer_height", h)) for h in core]
    core_li = [safe_val(get_val("lifted_index", h), 5) for h in core]
    core_cc_low = [safe_val(get_val("cloud_cover_low", h), 50) for h in core]
    core_cc_mid = [safe_val(get_val("cloud_cover_mid", h), 50) for h in core]
    core_wind = [safe_val(get_val("wind_speed_10m", h)) for h in core]
    core_wind_dir = [get_val("wind_direction_10m", h) for h in core]
    core_temp = [get_val("temperature_2m", h) for h in core]
    core_dp = [get_val("dew_point_2m", h) for h in core]
    core_rad = [safe_val(get_val("direct_radiation", h)) for h in core]
    core_sm = [safe_val(get_val("soil_moisture_0_to_1cm", h), 0.25) for h in core]
    core_gusts = [safe_val(get_val("wind_gusts_10m", h)) for h in core]

    n = len(core_cape)
    avg_cape = sum(core_cape) / n
    max_cape = max(core_cape)
    avg_blh = sum(core_blh) / n
    max_blh = max(core_blh)
    avg_li = sum(core_li) / n
    min_li = min(core_li)
    avg_cc_low_mid = sum((l + m) / 2 for l, m in zip(core_cc_low, core_cc_mid)) / n
    avg_wind = sum(core_wind) / n
    max_gusts = max(core_gusts)

    spreads = [t - d for t, d in zip(core_temp, core_dp) if t is not None and d is not None]
    avg_spread = sum(spreads) / len(spreads) if spreads else 5
    avg_rad = sum(core_rad) / n
    avg_sm = sum(core_sm) / n

    # Previous rain
    prev_rain = sum(safe_val(get_val("precipitation", h)) for h in range(0, 9))
    if day_idx > 0:
        ps = (day_idx - 1) * 24
        for h in range(12, 24):
            idx = ps + h
            if idx < len(hourly.get("precipitation", [])):
                prev_rain += safe_val(hourly["precipitation"][idx])

    # --- SCORING ---
    s_cape = score_param(avg_cape, thresholds["cape"])
    s_blh = score_param(avg_blh, thresholds["boundary_layer_height_agl"])
    s_li = score_param(avg_li, thresholds["lifted_index"])
    s_cc = score_param(avg_cc_low_mid, thresholds["cloud_cover_low_mid"], invert=True)
    s_wind = score_param(avg_wind, thresholds["wind_speed_10m"], invert=True)
    s_spread = score_param(avg_spread, thresholds["temp_spread"])
    s_rad = score_param(avg_rad, thresholds["direct_radiation"])
    s_sm = score_param(avg_sm, thresholds["soil_moisture"], invert=True)

    if prev_rain <= 0.5:
        s_rain = 3.0
    elif prev_rain <= 3:
        s_rain = 2.0
    elif prev_rain <= 10:
        s_rain = 1.0
    else:
        s_rain = 0.0

    raw = (s_cape * weights["cape"] + s_blh * weights["boundary_layer_height"] +
           s_li * weights["lifted_index"] + s_cc * weights["cloud_cover"] +
           s_wind * weights["wind"] + s_spread * weights["temp_spread"] +
           s_rad * weights["radiation"] + s_sm * weights["soil_moisture"] +
           s_rain * weights["previous_rain"])
    final_score = round(min(10, max(0, raw / 3.0 * 10)), 1)

    # --- BONUSES & PENALTIES ---
    warnings = []
    bonuses = []
    alpine = scoring["alpine_specifics"]

    # Cu-Thermal bonus
    cu = alpine["cu_thermal_ideal"]
    if cu["cloud_cover_range"][0] <= avg_cc_low_mid <= cu["cloud_cover_range"][1] and avg_cape >= cu["cape_min"]:
        bonuses.append("Cu-Thermik erwartet (markierte Aufwinde)")
        final_score = min(10, final_score + 0.5)

    # Thunderstorm warning
    ts = alpine["thunderstorm_warning"]
    if max_cape >= ts["cape_threshold"] or min_li <= ts["lifted_index_threshold"]:
        warnings.append(f"⚠️ Überentwicklung/Gewitter möglich (CAPE {max_cape:.0f}, LI {min_li:.1f})")
        final_score = min(final_score, 7)

    # Föhn detection — only for alpine regions
    if region_type == "alpine":
        valid_dirs = [d for d in core_wind_dir if d is not None]
        avg_wind_dir = sum(valid_dirs) / len(valid_dirs) if valid_dirs else 0
        wind80 = [safe_val(get_val("wind_speed_80m", h)) for h in core]
        avg_wind80 = sum(wind80) / len(wind80)
        foehn = alpine["foehn_detection"]
        if (foehn["wind_direction_700hpa_range"][0] <= avg_wind_dir <= foehn["wind_direction_700hpa_range"][1]
                and avg_wind80 >= foehn["wind_speed_700hpa_min_kmh"]):
            warnings.append("🌬️ Föhn-Lage erkannt – Wellenflug statt Thermik möglich")
    else:
        valid_dirs = [d for d in core_wind_dir if d is not None]
        avg_wind_dir = sum(valid_dirs) / len(valid_dirs) if valid_dirs else 0

    if avg_wind > 30:
        warnings.append(f"💨 Starker Bodenwind ({avg_wind:.0f} km/h) – Thermik zerfetzt")
    if max_gusts > 50:
        warnings.append(f"💨 Böen bis {max_gusts:.0f} km/h!")

    # --- PHASE ANALYSIS ---
    phases = {}
    for pk, pc in phases_config.items():
        ph = range(pc["start"], pc["end"])
        ph_cape = [safe_val(get_val("cape", h)) for h in ph]
        ph_blh = [safe_val(get_val("boundary_layer_height", h)) for h in ph]
        ph_cc = [safe_val(get_val("cloud_cover", h), 50) for h in ph]
        ph_wind = [safe_val(get_val("wind_speed_10m", h)) for h in ph]
        ph_wind_d = [get_val("wind_direction_10m", h) for h in ph]
        ph_temp = [get_val("temperature_2m", h) for h in ph]
        ph_dp = [get_val("dew_point_2m", h) for h in ph]

        pn = len(ph_cape) or 1
        pa_cape = sum(ph_cape) / pn
        pa_blh = sum(ph_blh) / pn
        pa_cc = sum(ph_cc) / pn
        pa_wind = sum(ph_wind) / pn
        vd = [d for d in ph_wind_d if d is not None]
        pa_wd = sum(vd) / len(vd) if vd else 0

        cc_low_ph = [safe_val(get_val("cloud_cover_low", h), 30) for h in ph]
        climb = estimate_climb_rate(pa_cape, pa_blh, sum(cc_low_ph) / pn, pa_wind)

        bases = [estimate_cloud_base_msl(t, d, elevation) for t, d in zip(ph_temp, ph_dp)]
        bases = [b for b in bases if b is not None]
        avg_base = round(sum(bases) / len(bases)) if bases else None

        ps = (score_param(pa_cape, thresholds["cape"]) * 0.4 +
              score_param(pa_blh, thresholds["boundary_layer_height_agl"]) * 0.4 +
              score_param(pa_cc, thresholds["cloud_cover_low_mid"], invert=True) * 0.2)
        ps_norm = round(min(5, max(0, ps / 3.0 * 5)))

        phases[pk] = {
            "label": pc["label"],
            "hours": f"{pc['start']:02d}-{pc['end']:02d}",
            "score_dots": ps_norm,
            "avg_cape": round(pa_cape),
            "avg_blh": round(pa_blh),
            "avg_cloud_cover": round(pa_cc),
            "avg_wind_kmh": round(pa_wind, 1),
            "avg_wind_direction": wind_direction_name(pa_wd),
            "estimated_climb_ms": climb,
            "cloud_base_msl": avg_base,
        }

    best_phase = max(phases.items(), key=lambda x: x[1]["score_dots"])
    dom_wind_dir = wind_direction_name(avg_wind_dir)

    # Cloud description
    if avg_cc_low_mid < 10:
        cloud_desc = "Blauthermik – keine konvektiven Wolken"
    elif avg_cc_low_mid < 30 and avg_cape > 200:
        cb = phases.get("early_afternoon", {}).get("cloud_base_msl", "?")
        cloud_desc = f"Cu-Thermik, Basis ca. {cb}m MSL"
    elif avg_cc_low_mid < 50:
        cloud_desc = "Teilweise bewölkt, Thermik zwischen den Wolken"
    elif avg_cc_low_mid < 70:
        cloud_desc = "Stärkere Bewölkung – Thermik eingeschränkt durch Abschattung"
    else:
        cloud_desc = "Stark bewölkt – kaum Thermik zu erwarten"

    if avg_sm < 0.10:
        soil_desc = "Sehr trocken – hervorragende Thermik-Bedingungen"
    elif avg_sm < 0.20:
        soil_desc = "Trocken – gute Bedingungen"
    elif avg_sm < 0.30:
        soil_desc = "Mäßig feucht"
    elif avg_sm < 0.40:
        soil_desc = "Feucht – Thermik verzögert"
    else:
        soil_desc = "Sehr feucht/nass – schwache Thermik"
    if prev_rain > 5:
        soil_desc += f" (Regen Vortag: {prev_rain:.1f}mm)"

    return {
        "date": date_str,
        "weekday": weekday_de,
        "score": final_score,
        "score_int": round(final_score),
        "sub_scores": {
            "cape": round(s_cape, 2), "blh": round(s_blh, 2),
            "lifted_index": round(s_li, 2), "cloud_cover": round(s_cc, 2),
            "wind": round(s_wind, 2), "spread": round(s_spread, 2),
            "radiation": round(s_rad, 2), "soil_moisture": round(s_sm, 2),
            "prev_rain": round(s_rain, 2),
        },
        "metrics": {
            "avg_cape": round(avg_cape), "max_cape": round(max_cape),
            "avg_blh_agl": round(avg_blh), "max_blh_agl": round(max_blh),
            "avg_lifted_index": round(avg_li, 1), "min_lifted_index": round(min_li, 1),
            "avg_cloud_cover_low_mid": round(avg_cc_low_mid),
            "avg_wind_kmh": round(avg_wind, 1), "max_gusts_kmh": round(max_gusts, 1),
            "wind_direction": dom_wind_dir,
            "avg_temp_spread": round(avg_spread, 1),
            "avg_direct_radiation": round(avg_rad),
            "avg_soil_moisture": round(avg_sm, 3),
            "previous_rain_mm": round(prev_rain, 1),
        },
        "descriptions": {"clouds": cloud_desc, "soil": soil_desc},
        "phases": phases,
        "best_phase": best_phase[0],
        "warnings": warnings,
        "bonuses": bonuses,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Segelflug-Thermikvorhersage (Multi-Region)")
    parser.add_argument("--list-regions", action="store_true", help="Verfügbare Regionen auflisten")
    parser.add_argument("--region", type=str, help="Region-ID (z.B. werdenfels, inntal, wasserkuppe)")
    parser.add_argument("--lat", type=float, help="Latitude (eigene Koordinaten)")
    parser.add_argument("--lon", type=float, help="Longitude (eigene Koordinaten)")
    parser.add_argument("--name", type=str, help="Standortname (bei eigenen Koordinaten)")
    parser.add_argument("--elevation", type=int, help="Platzhöhe in Metern MSL (Standard: 500)")
    parser.add_argument("--type", type=str, choices=["alpine", "mittelgebirge", "flachland"],
                        help="Geländetyp (Standard: alpine)")
    parser.add_argument("--dhv-region", type=str, help="DHV-Region (Deutschland/Nordalpen/Südalpen)")
    parser.add_argument("--days", type=int, default=3, help="Vorhersagetage (1-7, Standard: 3)")
    parser.add_argument("--no-dhv", action="store_true", help="DHV-Wetter nicht abrufen")
    args = parser.parse_args()

    config = load_config()

    # List regions mode
    if args.list_regions:
        list_regions(config)
        return

    # Resolve location
    location = resolve_region(args, config)
    lat = location["latitude"]
    lon = location["longitude"]
    days = min(7, max(1, args.days))
    region_type = location["type"]

    # Select model based on region type
    model_pref = config["api"]["model_preference"]
    model = model_pref.get(region_type, config["api"].get("fallback_model", "icon_d2"))

    print(f"[INFO] Region: {location['name']} ({lat}°N, {lon}°E)", file=sys.stderr)
    print(f"[INFO] Modell: {model}, Tage: {days}, Typ: {region_type}", file=sys.stderr)

    # Fetch weather data
    try:
        data = fetch_open_meteo(lat, lon, days, model)
    except Exception as e:
        print(json.dumps({"error": str(e), "type": "api_fetch_failed"}))
        sys.exit(1)

    if "hourly" not in data:
        print(json.dumps({"error": "No hourly data in API response", "raw_keys": list(data.keys())}))
        sys.exit(1)

    hourly = data["hourly"]

    # Analyze each day
    forecast_days = []
    for day_idx in range(days):
        try:
            day_result = analyze_day(hourly, day_idx, config, location)
            forecast_days.append(day_result)
        except Exception as e:
            forecast_days.append({"date": f"day_{day_idx}", "error": str(e)})

    # DHV integration
    dhv_data = None
    dhv_available = False
    if not args.no_dhv:
        dhv_data = fetch_dhv_data(location.get("dhv_region", "Deutschland"))
        if dhv_data and dhv_data.get("forecasts"):
            dhv_available = True
            # Check for severe DHV warnings vs algo score
            for fc in dhv_data["forecasts"]:
                if fc.get("score", 3) <= 2:  # DHV says bad/storm
                    for day in forecast_days:
                        if "score" in day and day["score"] >= 6:
                            day["warnings"].append(
                                f"⚠️ DHV-Warnung: {fc.get('title', 'Schlechtwetter')} – Score nach unten korrigiert"
                            )
                            day["score"] = min(day["score"], 5)
                            day["score_int"] = round(day["score"])

    valid_days = [d for d in forecast_days if "score" in d]
    best_day = max(valid_days, key=lambda d: d["score"]) if valid_days else None

    result = {
        "location": {
            "id": location["id"],
            "name": location["name"],
            "latitude": lat,
            "longitude": lon,
            "elevation_m": location["elevation_m"],
            "type": region_type,
        },
        "model": model,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "forecast_days": days,
        "days": forecast_days,
        "best_day": best_day["date"] if best_day else None,
        "best_score": best_day["score"] if best_day else 0,
        "dhv_available": dhv_available,
        "dhv": dhv_data if dhv_available else None,
        "detail_links": config["output"]["detail_links"],
        "score_labels": config["output"]["score_labels"],
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
