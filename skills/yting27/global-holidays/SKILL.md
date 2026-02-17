---
name: holidays
description: |
  Use this skill whenever a task involves checking, generating, or working with public holidays — for any country or subdivision (state, province, region). Triggers include: "is [date] a holiday?", "list all holidays in [country/year]", "find holidays in [date range]", "working days", "business days", "skip holidays", "holiday calendar", or any task that requires knowing whether a date is a government-designated public holiday. Also use when combining public holidays with custom or personal holiday dates. Do NOT use for general date arithmetic, timezone conversion, or calendar rendering unless holidays are explicitly involved.
---

# holidays — Python Holiday Library

## Overview

`holidays` is a Python library that generates country- and subdivision-specific sets of government-designated holidays on the fly. It covers 249 countries (ISO 3166-1) and supports subdivisions (states, provinces, regions) via ISO 3166-2 codes.

The central object is `HolidayBase`, which behaves like a Python `dict` mapping `date → holiday name`. All examples below can be run directly in the shell:

```bash
python <<'EOF'
# your code here
EOF
```

---

## Installation

```bash
pip install --upgrade holidays
```

For the latest development version:

```bash
pip install --upgrade https://github.com/vacanza/holidays/tarball/dev
```

---

## Quick Reference

| Task | Method |
|------|--------|
| All holidays for a country/year | `country_holidays('US', years=2024)` |
| Holidays for a subdivision | `country_holidays('US', subdiv='CA', years=2024)` |
| Holidays in a date range | `holidays_obj['2024-01-01':'2024-01-31']` |
| Check if a date is a holiday | `holidays_obj.get('2024-12-25')` → name or `None` |
| Add custom holidays | `holidays_obj.update({'2024-07-10': 'My Birthday!'})` |
| List all supported countries | `list_supported_countries()` |
| List countries with localization | `list_localized_countries()` |

---

## Core API

### `country_holidays()` — Main Function

```python
country_holidays(
    country,          # ISO 3166-1 alpha-2 code, e.g. 'US', 'GB', 'DE'
    subdiv=None,      # ISO 3166-2 subdivision code, e.g. 'CA', 'TX', 'BY'
    years=None,       # int or list of ints, e.g. 2024 or [2023, 2024]
    expand=True,      # auto-expand years when checking dates outside current range
    observed=True,    # include observed holidays (e.g. holiday on weekend → Monday)
    language=None,    # ISO 639-1 language code for holiday names, e.g. 'en', 'de'
    categories=None,  # filter to specific holiday categories (country-dependent)
)
```

Returns a `HolidayBase` object (dict-like: `{date: name}`).

---

## Common Tasks

### 1. Get All Holidays for a Country in a Year

```python
from holidays import country_holidays

us_holidays = country_holidays('US', years=2024)
for date, name in sorted(us_holidays.items()):
    print(date, name)
```

### 2. Get Holidays for a Subdivision (State / Province)

Use the ISO 3166-2 subdivision code (e.g. `'CA'` for California, `'BY'` for Bavaria).

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA', years=2024)
for date, name in sorted(ca_holidays.items()):
    print(date, name)
```

### 3. Get Holidays Within a Date Range

Slice the `HolidayBase` object with date strings (`'YYYY-MM-DD'`):

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA', years=2024)
for day in ca_holidays['2024-01-01':'2024-01-31']:
    print(f"{day}: {ca_holidays.get(day)}")
```

### 4. Check if a Specific Date is a Holiday

`.get()` returns the holiday name if the date is a holiday, or `None` if it is not.

```python
from holidays import country_holidays

ca_holidays = country_holidays('US', subdiv='CA')

# Is December 25 a holiday?
name = ca_holidays.get('2024-12-25')
print(name)   # → 'Christmas Day'

# Is December 26 a holiday?
name = ca_holidays.get('2024-12-26')
print(name)   # → None
```

**Tip:** Use `if date in holidays_obj:` for a boolean check (faster than `.get()`).

### 5. Working with Custom Holidays

Custom holidays are stored as a JSON file at `$HOME/openclaw-personal/custom-holidays.json`:

```json
{
  "2024-07-10": "My Birthday!",
  "2024-10-01": "Family Celebration"
}
```

Load and merge with a country's calendar using `.update()`:

```python
import json
from pathlib import Path
from holidays import country_holidays

custom_file = Path("~/openclaw-personal/custom-holidays.json").expanduser()
with open(custom_file) as f:
    custom_data = json.load(f)

holidays_2024 = country_holidays('US', years=2024)
holidays_2024.update(custom_data)

print(holidays_2024.get('2024-07-10'))  # → 'My Birthday!'
```

### 6. List All Supported Countries and Subdivisions

```python
from holidays import list_supported_countries

# include_aliases=True also returns common aliases (e.g. 'UK' for 'GB')
supported = list_supported_countries(include_aliases=True)
print(supported['US'])   # → list of supported US subdivision codes
```

### 7. Use Localized (Translated) Holiday Names

Some countries support multiple languages for holiday name output.

```python
from holidays import list_localized_countries, country_holidays

localized = list_localized_countries(include_aliases=True)

# Get supported languages for Malaysia
langs = localized['MY']   # e.g. ['en_MY', 'ms_MY', 'zh_CN']

# Generate holidays in the first available language
for date, name in sorted(country_holidays('MY', years=2025, language=langs[0]).items()):
    print(date, name)
```

---

## Key Behaviours to Know

- **`observed=True` (default):** When a holiday falls on a weekend, the observed date (typically Monday) is included. Set `observed=False` to get only the statutory date.
- **`expand=True` (default):** If you check a date outside the `years` range, the library automatically adds that year. Set `expand=False` to prevent this.
- **Multiple years:** Pass a list to `years` to load several years at once: `years=[2023, 2024, 2025]`.
- **Date keys:** The `HolidayBase` dict accepts `datetime.date`, `datetime.datetime`, or `'YYYY-MM-DD'` strings interchangeably as keys.
- **Country codes:** Use ISO 3166-1 alpha-2 (e.g. `'US'`, `'GB'`, `'DE'`). Aliases like `'UK'` are supported when `include_aliases=True`.

---

## Dependencies

- **Python:** 3.8+
- **Package:** `holidays` (PyPI). Install with `pip install --upgrade holidays`.
- No external system dependencies required.
