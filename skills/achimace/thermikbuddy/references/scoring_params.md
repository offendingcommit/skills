# Scoring-Parameter Referenz

## Gewichtete Parameter (0–10 Gesamtscore)

| # | Parameter | Gewicht | Quelle | Invertiert? |
|---|-----------|---------|--------|-------------|
| 1 | CAPE (J/kg) | 15% | Open-Meteo | Nein |
| 2 | Grenzschichthöhe BLH (m AGL) | 20% | Open-Meteo | Nein |
| 3 | Lifted Index | 10% | Open-Meteo | Nein |
| 4 | Bewölkung low+mid (%) | 15% | Open-Meteo | Ja |
| 5 | Wind 10m (km/h) | 10% | Open-Meteo | Ja |
| 6 | Temperatur-Spread T-Td (°C) | 5% | Berechnet | Nein |
| 7 | Direkte Strahlung (W/m²) | 10% | Open-Meteo | Nein |
| 8 | Bodenfeuchte 0-1cm (m³/m³) | 10% | Open-Meteo | Ja |
| 9 | Vortages-Regen (mm) | 5% | Open-Meteo | Ja |

## Schwellwerte

### CAPE (Convective Available Potential Energy)
- Poor: 0–50 J/kg
- OK: 50–150 J/kg
- Good: 150–400 J/kg
- Very Good: 400–900 J/kg
- Excellent: 900–1500 J/kg
- **Gewitterwarnung:** >2000 J/kg

### Grenzschichthöhe (BLH)
- Poor: 0–500m → kaum Thermik, sehr niedrige Arbeitshöhe
- OK: 500–1000m → schwache Platzrundthermik
- Good: 1000–1800m → solide Thermik, 30-50km Flüge
- Very Good: 1800–2500m → gute Streckenbedingungen
- Excellent: 2500–4000m → Hammertag, lange Strecken

### Lifted Index
- Poor: >2 → stabile Schichtung, keine Thermik
- OK: 0 bis 2 → schwach labil
- Good: -2 bis 0 → gute Labilität
- Very Good: -4 bis -2 → starke Labilität
- Excellent: -8 bis -4 → sehr starke Konvektion
- **Gewitterwarnung:** <-6

## Regionstypen

### Alpine Regionen
- Föhn-Erkennung aktiv (Südwind >25 km/h in 80m)
- Überentwicklungs-Warnungen
- Cu-Thermik-Bonus bei 15-50% Bewölkung + CAPE >300
- DHV Nordalpen/Südalpen als Validierung

### Mittelgebirge
- Keine Föhn-Erkennung
- Standard-BLH-Schwellwerte
- DHV Deutschland als Validierung

### Flachland
- Keine Föhn-Erkennung
- Typisch höhere BLH im Sommer
- DHV Deutschland als Validierung

## Steigwert-Schätzung

```
w ≈ √(2·CAPE) × 0.04 × BLH_factor × CloudCover_factor × Wind_factor
```

- BLH_factor: min(BLH/2000, 1.5)
- CC_factor: max(0.3, 1.0 - CC_low/150)
- Wind_factor: max(0.3, 1.0 - max(0, Wind-15)/40)
- Ergebnis: 0–5 m/s, typisch 0.8–2.2 m/s

## Wolkenbasis-Schätzung

```
Basis_MSL = Platzhöhe + (T - Td) × 125 m/°C
```

## Datenquellen

- **Open-Meteo API**: Kostenlos, ICON-D2 (2km Auflösung), ICON-EU Fallback
- **DHV Wetter**: Meteorologe Volker Schwaniz, 2× täglich aktualisiert
