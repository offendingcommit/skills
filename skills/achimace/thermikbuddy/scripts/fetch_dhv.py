#!/usr/bin/env python3
"""
DHV-Wetter-Scraper: Holt Segelflug-/Gleitschirmwetter von dhv.de
und klassifiziert die Vorhersagen auf einer 1–5 Skala.
Unterstützt Regions-Filter: Deutschland, Nordalpen, Südalpen.
"""

import json
import sys
import re
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser


DHV_URL = "https://www.dhv.de/wetter/dhv-wetter/"


class DHVParser(HTMLParser):
    """Simple HTML parser to extract forecast blocks from DHV weather page."""

    def __init__(self):
        super().__init__()
        self.in_content = False
        self.current_tag = None
        self.depth = 0
        self.text_blocks = []
        self.current_text = []
        self.capture = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        # Look for main content area
        if tag == "div" and ("wetter" in cls.lower() or "forecast" in cls.lower()
                             or "content" in cls.lower()):
            self.capture = True
        if self.capture:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.capture:
            self.depth -= 1
            if self.depth <= 0:
                if self.current_text:
                    self.text_blocks.append(" ".join(self.current_text))
                    self.current_text = []
                self.capture = False
                self.depth = 0

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_blocks.append(text)
            if self.capture:
                self.current_text.append(text)


def fetch_dhv_html():
    """Fetch DHV weather page HTML."""
    req = Request(DHV_URL, headers={
        "User-Agent": "Mozilla/5.0 (SoaringWeather/2.0)",
        "Accept-Language": "de-DE,de;q=0.9",
    })
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        print(f"[ERROR] Could not fetch DHV page: {e}", file=sys.stderr)
        return None


def extract_forecasts(html):
    """Extract forecast text blocks and try to associate with regions."""
    if not html:
        return []

    # Try structured parsing first
    parser = DHVParser()
    parser.feed(html)

    # Combine all text for regex-based extraction
    full_text = html

    # Remove HTML tags for text analysis
    clean = re.sub(r"<[^>]+>", " ", full_text)
    clean = re.sub(r"\s+", " ", clean)

    forecasts = []

    # Pattern: find region headers followed by forecast text
    # DHV typically structures: Region name → day forecasts
    regions_patterns = {
        "Deutschland": [
            r"(?:Deutschland|Deutschlandwetter|Bundesgebiet)(.*?)(?=Nordalpen|Südalpen|Süd[\s-]?alpen|$)",
        ],
        "Nordalpen": [
            r"(?:Nordalpen|Nördliche Alpen|Nord[\s-]?Alpen|Alpenrand)(.*?)(?=Südalpen|Süd[\s-]?alpen|Deutschland|$)",
        ],
        "Südalpen": [
            r"(?:Südalpen|Südliche Alpen|Süd[\s-]?Alpen)(.*?)(?=Nordalpen|Deutschland|$)",
        ],
    }

    for region, patterns in regions_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, clean, re.IGNORECASE | re.DOTALL)
            for match in matches:
                text = match.strip()
                if len(text) > 30:  # Skip too-short fragments
                    # Try to split by day indicators
                    day_splits = re.split(
                        r"(?=(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag|Heute|Morgen)[\s:,])",
                        text
                    )
                    for ds in day_splits:
                        ds = ds.strip()
                        if len(ds) > 20:
                            # Extract day name if present
                            day_match = re.match(
                                r"(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag|Heute|Morgen)",
                                ds
                            )
                            day_name = day_match.group(1) if day_match else None
                            forecasts.append({
                                "region": region,
                                "day": day_name,
                                "text": ds[:500],  # Limit text length
                            })

    # Fallback: if no structured data found, use raw text blocks
    if not forecasts and parser.text_blocks:
        combined = " ".join(parser.text_blocks)
        if len(combined) > 50:
            forecasts.append({
                "region": "Deutschland",
                "day": None,
                "text": combined[:500],
            })

    return forecasts


def classify_forecast(text):
    """
    Classify a forecast text on a 1–5 scale.
    1 = Sturm/gefährlich, 2 = schlecht, 3 = eingeschränkt, 4 = gut, 5 = sehr gut
    """
    text_lower = text.lower()

    # Weighted keyword scoring
    negative_strong = [  # -3 each
        "sturm", "stürmisch", "gewitter", "starkregen", "orkan",
        "unwetter", "hagel", "gefährlich", "starker wind", "kein flugwetter",
    ]
    negative_medium = [  # -2 each
        "regen", "regnerisch", "niederschlag", "stark bewölkt",
        "bedeckt", "kaltfront", "front", "schauer", "böig",
        "windig", "starkwind", "turbulent",
    ]
    negative_light = [  # -1 each
        "bewölkt", "wolkig", "aufziehend", "feucht", "nebel",
        "hochnebel", "restbewölkung", "eingeschränkt", "mäßig",
    ]
    positive_strong = [  # +3 each
        "starke thermik", "sehr gute thermik", "exzellent",
        "hammertag", "streckenflug", "gute basis", "cumulus",
        "hervorragend", "perfekt",
    ]
    positive_medium = [  # +2 each
        "thermik", "aufwind", "sonnig", "freundlich", "trocken",
        "gute bedingungen", "schwacher wind", "aufgelockert",
        "heiter", "wolkenlos",
    ]
    positive_light = [  # +1 each
        "sonne", "warm", "leichter wind", "teilweise",
        "wechselnd", "abklingend", "besserung",
    ]

    score = 0
    for kw in negative_strong:
        if kw in text_lower:
            score -= 3
    for kw in negative_medium:
        if kw in text_lower:
            score -= 2
    for kw in negative_light:
        if kw in text_lower:
            score -= 1
    for kw in positive_strong:
        if kw in text_lower:
            score += 3
    for kw in positive_medium:
        if kw in text_lower:
            score += 2
    for kw in positive_light:
        if kw in text_lower:
            score += 1

    # Map raw score to 1–5
    if score <= -5:
        return 1
    elif score <= -2:
        return 2
    elif score <= 2:
        return 3
    elif score <= 5:
        return 4
    else:
        return 5


SCORE_LABELS = {
    1: "🔴 Sturm/Gefährlich",
    2: "🟠 Schlecht",
    3: "🟡 Eingeschränkt",
    4: "🟢 Gut",
    5: "🟢🟢 Sehr gut",
}


def fetch_and_classify(region_filter=None):
    """
    Main entry: fetch DHV page, extract & classify forecasts.
    region_filter: "Nordalpen", "Südalpen", "Deutschland", or None for all.
    Returns dict with forecasts and metadata.
    """
    html = fetch_dhv_html()
    if not html:
        return {"error": "Could not fetch DHV weather page", "forecasts": []}

    raw_forecasts = extract_forecasts(html)

    # Apply region filter
    if region_filter:
        filtered = [f for f in raw_forecasts if f["region"].lower() == region_filter.lower()]
        if not filtered:
            # Fallback: include Deutschland as backup
            filtered = [f for f in raw_forecasts if f["region"] == "Deutschland"]
        forecasts = filtered
    else:
        forecasts = raw_forecasts

    # Classify each forecast
    results = []
    for fc in forecasts:
        score = classify_forecast(fc["text"])
        results.append({
            "region": fc["region"],
            "day": fc.get("day"),
            "title": fc.get("day", fc["region"]),
            "text": fc["text"],
            "score": score,
            "score_label": SCORE_LABELS.get(score, "?"),
        })

    return {
        "source": "DHV Wetter (dhv.de)",
        "url": DHV_URL,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "region_filter": region_filter,
        "forecasts": results,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DHV-Wetter Scraper")
    parser.add_argument("--region", type=str, default=None,
                        help="Region filter: Deutschland, Nordalpen, Südalpen")
    parser.add_argument("--raw", action="store_true", help="Show raw HTML blocks")
    args = parser.parse_args()

    result = fetch_and_classify(region_filter=args.region)
    print(json.dumps(result, ensure_ascii=False, indent=2))
