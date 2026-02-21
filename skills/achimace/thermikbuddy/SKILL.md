---
name: soaring-weather
description: Segelflug- und Thermikvorhersage mit Thermik-Score (0–10). Nutze diesen Skill wenn der User nach Segelflugwetter, Thermik, Streckenflugbedingungen, Flugwetter für Segelflieger oder Gleitschirmflieger fragt – auch indirekt wie "lohnt sich Samstag fliegen?", "wie wird die Thermik?", "Segelflugwetter Wochenende?" oder "kann ich am Sonntag einen Streckenflug machen?". Der Skill fragt nach Region/Standort, ruft Open-Meteo (ICON-D2) und DHV-Wetter ab und liefert eine Profi-Einschätzung mit Tagesablauf, Steigwerten, Basishöhe und Warnungen.
version: 1.0.0
metadata: {"openclaw":{"emoji":"🪂","requires":{"bins":["python3"],"env":[]},"homepage":"https://github.com/soaring-weather/openclaw-skill"}}
---

# Soaring Weather – Thermikvorhersage für Segelflieger

Dieser Skill liefert eine fundierte Segelflug-Thermikvorhersage mit Score 0–10,
Tagesablauf in 4 Phasen, Steigwert-Schätzung, Basishöhe und DHV-Wetterintegration.

## Schritt 1: Region erfragen

Bevor du die Vorhersage abrufst, frage den User nach der gewünschten Region.
Zeige die verfügbaren Regionen aus der Konfiguration:

```bash
python3 {baseDir}/scripts/run_forecast.py --list-regions
```

Das gibt die verfügbaren Regionen als JSON-Liste aus. Stelle dem User die Optionen
zur Auswahl, z.B.:

> Für welche Region möchtest du die Thermikvorhersage?
> 1. 🏔️ Werdenfels / Bayerischer Alpenordrand
> 2. 🏔️ Inntal / Nordtiroler Alpen
> 3. ⛰️ Schwäbische Alb
> 4. 🌄 Schwarzwald
> 5. 🌾 Norddeutsches Flachland
> 6. 📍 Eigene Koordinaten eingeben

Falls der User bereits eine Region oder Koordinaten nennt ("Thermik in Innsbruck",
"Segelflugwetter Wasserkuppe"), überspringe die Frage und wähle die passende Region
oder verwende die genannten Koordinaten direkt.

## Schritt 2: Vorhersage abrufen

Starte das Forecast-Script mit der gewählten Region:

```bash
python3 {baseDir}/scripts/run_forecast.py --region <region_id>
```

Oder mit eigenen Koordinaten:

```bash
python3 {baseDir}/scripts/run_forecast.py --lat <lat> --lon <lon> --name "Standortname"
```

Optionale Parameter:
- `--days 3` (1–7, Standard: 3)
- `--no-dhv` (DHV-Wetter überspringen)

Das Script gibt JSON auf stdout aus (Logs gehen auf stderr).

## Schritt 3: Ergebnis formatieren

Formatiere die JSON-Ausgabe für den User. Verwende dieses Template:

### Tagesübersicht (pro Tag)

```
[Emoji] THERMIK-VORHERSAGE – [Standortname]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 [Wochentag], [Datum]
🏆 SCORE: [X]/10 — [Bewertungstext]

🌡️ Thermik-Kern:
   Steigwerte: ~[X] m/s | Basis: [X]m MSL
   CAPE: [X] J/kg | BLH: [X]m AGL

☁️ [Wolken-Beschreibung]
💨 Wind: [Richtung] [Geschwindigkeit] km/h
🌍 Boden: [Feuchte-Bewertung]
⚠️ [Warnungen falls zutreffend]

📊 Tagesablauf:
   09-12: [●-Balken] [Kurzbeschreibung]
   12-15: [●-Balken] [Kurzbeschreibung]
   15-18: [●-Balken] [Kurzbeschreibung]
   18-20: [●-Balken] [Kurzbeschreibung]
```

### Score-Emoji-Zuordnung
- 0–2: ❌ Kein Segelflugwetter
- 3–4: 🌥️ Eingeschränkt
- 5–6: ⛅ Ordentlicher Tag
- 7–8: ☀️ Guter Tag
- 9–10: 🔥 Hammertag!

Verwende ◉ für aktive und ◎ für inaktive Kreise (5 pro Phase).

### DHV-Wetter-Block

Wenn DHV-Daten verfügbar sind (Feld `dhv_available: true`), zeige zusätzlich:

```
━━━ DHV WETTER – [Region] ━━━
Stand: [Zeitstempel]

[🔴/🟠/🟡/🟢] [Tag]: [Titel]
   [Beschreibung]
   💨 [Wind]
```

Hinweis: Die DHV-Thermikvorhersage macht von Oktober bis März Winterpause.
Wind- und Sturmwarnungen bleiben auch im Winter relevant.

### Detail-Links

Am Ende immer anbieten:
- DHV Wetter: https://www.dhv.de/wetter/dhv-wetter/
- SkySight: https://skysight.io
- TopMeteo: https://europe.topmeteo.eu/de/
- DWD Segelflug: https://www.dwd.de/DE/fachnutzer/luftfahrt/kg_segel/segel_node.html
- aufwin.de: https://aufwin.de
- Soaringmeteo (WRF 2km): https://soaringmeteo.org/v2

## Hinweise zum Score

Der Score berücksichtigt 9 gewichtete Parameter: CAPE, Grenzschichthöhe (BLH),
Lifted Index, Bewölkung, Wind, Temperatur-Spread, Einstrahlung, Bodenfeuchte und
Vortages-Niederschlag. Details siehe `{baseDir}/references/scoring_params.md`.

Regionsspezifische Anpassungen:
- **Alpenregionen:** Föhn-Erkennung, Überentwicklungs-Warnung, Cu-Thermik-Bonus
- **Flachland:** Keine Föhn-Erkennung, andere BLH-Schwellwerte
- **Mittelgebirge:** Moderate Anpassungen

Die DHV-Experten-Einschätzung (2× täglich von Meteorologe Volker Schwaniz) dient als
Validierung und kann den algorithmischen Score bei starken Abweichungen korrigieren –
insbesondere bei Wind-/Sturmwarnungen (Sicherheit geht vor).
