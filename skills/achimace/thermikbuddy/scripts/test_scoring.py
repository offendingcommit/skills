#!/usr/bin/env python3
"""Test scoring with mock data for different region types."""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_forecast import analyze_day, load_config, list_regions


def make_mock_hourly(days=1, cape=500, blh=2000, li=-2, cc_low=20, cc_mid=15,
                     wind=12, wind_dir=270, temp=25, dp=12, rad=700,
                     sm=0.15, precip=0, gusts=20, wind80=15):
    """Generate mock hourly data."""
    n = days * 24
    return {
        "time": [f"2026-07-15T{h%24:02d}:00" for h in range(n)],
        "temperature_2m": [temp] * n,
        "dew_point_2m": [dp] * n,
        "relative_humidity_2m": [50] * n,
        "precipitation": [precip] * n,
        "rain": [0] * n,
        "cloud_cover": [cc_low + cc_mid] * n,
        "cloud_cover_low": [cc_low] * n,
        "cloud_cover_mid": [cc_mid] * n,
        "cloud_cover_high": [10] * n,
        "wind_speed_10m": [wind] * n,
        "wind_speed_80m": [wind80] * n,
        "wind_direction_10m": [wind_dir] * n,
        "wind_direction_80m": [wind_dir] * n,
        "wind_gusts_10m": [gusts] * n,
        "cape": [cape] * n,
        "lifted_index": [li] * n,
        "convective_inhibition": [-10] * n,
        "boundary_layer_height": [blh] * n,
        "shortwave_radiation": [rad] * n,
        "direct_radiation": [rad] * n,
        "soil_moisture_0_to_1cm": [sm] * n,
        "soil_moisture_1_to_3cm": [sm * 1.2] * n,
        "soil_moisture_3_to_9cm": [sm * 1.5] * n,
        "soil_temperature_0cm": [temp - 3] * n,
    }


def test_scenario(name, config, location, **kwargs):
    hourly = make_mock_hourly(**kwargs)
    result = analyze_day(hourly, 0, config, location)
    score = result["score"]
    best = result["best_phase"]
    warnings = result["warnings"]
    bonuses = result["bonuses"]
    climb = result["phases"].get("early_afternoon", {}).get("estimated_climb_ms", "?")
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"  Region: {location['name']} ({location['type']})")
    print(f"{'='*60}")
    print(f"  Score:     {score}/10")
    print(f"  Steigwert: ~{climb} m/s")
    print(f"  Beste Phase: {best}")
    if bonuses:
        print(f"  Bonuses:   {', '.join(bonuses)}")
    if warnings:
        print(f"  Warnings:  {', '.join(warnings)}")
    print()
    return score


def main():
    config = load_config()

    # Test list-regions
    print("=== Verfügbare Regionen ===")
    list_regions(config)
    print()

    # Define test locations
    loc_alpine = {
        "id": "werdenfels", "name": "Werdenfels", "latitude": 47.48,
        "longitude": 11.10, "elevation_m": 700, "type": "alpine",
        "dhv_region": "Nordalpen",
    }
    loc_mittelgebirge = {
        "id": "wasserkuppe", "name": "Wasserkuppe", "latitude": 50.50,
        "longitude": 9.94, "elevation_m": 950, "type": "mittelgebirge",
        "dhv_region": "Deutschland",
    }
    loc_flachland = {
        "id": "luesse", "name": "Lüsse", "latitude": 52.14,
        "longitude": 12.67, "elevation_m": 70, "type": "flachland",
        "dhv_region": "Deutschland",
    }

    results = []

    # 1. Hammertag Alpine
    s = test_scenario("🔥 Hammertag – Werdenfels (Alpin)", config, loc_alpine,
                      cape=700, blh=2800, li=-3, cc_low=20, cc_mid=10,
                      wind=8, temp=28, dp=11, rad=850, sm=0.08, gusts=15)
    results.append(("Hammertag Alpine", s))

    # 2. Hammertag Flachland
    s = test_scenario("🔥 Hammertag – Lüsse (Flachland)", config, loc_flachland,
                      cape=700, blh=2800, li=-3, cc_low=20, cc_mid=10,
                      wind=8, temp=28, dp=11, rad=850, sm=0.08, gusts=15)
    results.append(("Hammertag Flachland", s))

    # 3. Durchschnitt Mittelgebirge
    s = test_scenario("⛅ Durchschnitt – Wasserkuppe", config, loc_mittelgebirge,
                      cape=350, blh=1600, li=-1, cc_low=30, cc_mid=25,
                      wind=15, temp=22, dp=13, rad=500, sm=0.22, gusts=25)
    results.append(("Durchschnitt Mittelgebirge", s))

    # 4. Schlechtwetter
    s = test_scenario("❌ Schlechtwetter – Werdenfels", config, loc_alpine,
                      cape=50, blh=600, li=3, cc_low=70, cc_mid=60,
                      wind=30, temp=14, dp=12, rad=100, sm=0.42, precip=8, gusts=55)
    results.append(("Schlechtwetter", s))

    # 5. Föhn-Lage (nur alpine Erkennung)
    s = test_scenario("🌬️ Föhn-Lage – Werdenfels (Alpin)", config, loc_alpine,
                      cape=200, blh=1500, li=0, cc_low=5, cc_mid=5,
                      wind=20, wind_dir=180, wind80=35, temp=20, dp=5,
                      rad=800, sm=0.12, gusts=40)
    results.append(("Föhn Alpine", s))

    # 6. Gleiche Windlage, aber Mittelgebirge → kein Föhn-Warning
    s = test_scenario("💨 Südwind – Wasserkuppe (kein Föhn)", config, loc_mittelgebirge,
                      cape=200, blh=1500, li=0, cc_low=5, cc_mid=5,
                      wind=20, wind_dir=180, wind80=35, temp=20, dp=5,
                      rad=800, sm=0.12, gusts=40)
    results.append(("Südwind Mittelgebirge", s))

    # Summary
    print("\n" + "="*60)
    print("  ZUSAMMENFASSUNG")
    print("="*60)
    for name, score in results:
        bar = "●" * round(score) + "○" * (10 - round(score))
        print(f"  {score:4.1f}/10 [{bar}] {name}")

    # Validate
    errors = 0
    if results[0][1] < 7:
        print("  ❌ FAIL: Hammertag Alpine sollte >= 7 sein")
        errors += 1
    if results[3][1] > 3:
        print("  ❌ FAIL: Schlechtwetter sollte <= 3 sein")
        errors += 1

    print(f"\n  {'✅ Alle Tests bestanden!' if errors == 0 else f'❌ {errors} Fehler'}")
    return errors


if __name__ == "__main__":
    sys.exit(main())
