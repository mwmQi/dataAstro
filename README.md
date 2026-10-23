# dataAstro

[![CI](https://github.com/mwmQi/dataAstro/actions/workflows/ci.yml/badge.svg)](https://github.com/mwmQi/dataAstro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

High-precision, deterministic Vedic Astrology calculation and Kundli extraction module powered by **Swiss Ephemeris** (`pyswisseph`) with standard **Lahiri (Chitrapaksha)** ayanamsa.

Built as an open, offline alternative to proprietary closed APIs (AstroSage, Horocosmo) — pure astronomical physics and classical Jyotish rules with zero external API calls, zero rate-limits, and zero subscription walls.

---

## Capabilities

| Domain | Scope |
|---|---|
| **Vedic Panchang** | Tithi, Paksha, Nakshatra + Pada + Lord, Yoga, Karana, Local Sunrise / Sunset, Ayanamsa |
| **Planetary Math** | 9 Grahas (Sun..Ketu): DMS degrees, absolute longitude, house occupancy, dignity (Exalted, Mooltrikona, Own, Friend, Neutral, Enemy, Debilitated), combustion, retrograde flags, daily speed |
| **Houses & Cusps** | Whole-Sign Bhavas + Placidus / KP Cusps for high-precision house division |
| **16 Divisional Charts** | D1 (Lagna), D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsha), D9 (Navamsha), D10 (Dashamsha / Career), D12, D16, D20, D24, D27, D30, D40, D45, D60 (Shashtiamsa) |
| **Ashtakavarga** | Bhinnashtakavarga per planet + Sarvashtakavarga (rigorously asserted to the 337 total constant) |
| **Shadbala** | Sthana, Dig, Kala, Cheshta, Naisargika strengths in Virupas and Rupas |
| **Vimshottari Dasha** | Birth balance, currently active Mahadasha / Antardasha / Pratyantardasha, and full 240-year multi-level tree |
| **Yogas & Doshas** | Classical Raja Yogas, Vipreet Raja Yoga, Budhaditya Yoga, Vargottama, and Sade Sati phase detection |
| **LLM Ready** | Pre-generated `ai_digest` paragraph designed for direct LLM system-prompt ingestion to prevent astrological hallucination |

---

## Installation

Install directly from GitHub via `pip`:

```bash
pip install git+https://github.com/mwmQi/dataAstro.git
```

Or clone for local development:

```bash
git clone https://github.com/mwmQi/dataAstro.git
cd dataAstro
pip install -r requirements.txt
pip install -e .
```

---

## Quickstart

### Python API

```python
from data_astro import get_person_details

# Birth details: Date (YYYY-MM-DD), Time (HH:MM:SS), Lat/Lon, Timezone (IST = +5.5)
chart = get_person_details(
    name="Prithvi Raj",
    dob="2007-03-13",
    tob="18:05:00",
    lat=25.51095,
    lon=86.47246,
    tz=5.5
)

# 1. Ready-to-use LLM digest:
print(chart["ai_digest"])

# 2. Inspect D10 Career Chart (10th house occupants & sign):
print("D10 10th House:", chart["divisional_charts"]["D10"]["houses"]["10"])

# 3. Active Dasha:
print("Current Dasha:", chart["dasha"]["current"])
```

### CLI Interface

```bash
# Calculate directly from terminal:
python3 -m data_astro --name "Prithvi Raj" --dob 2007-03-13 --tob 18:05:00 --lat 25.51095 --lon 86.47246 --out chart.json
```

### Standalone REST Server

```bash
uvicorn data_astro.core:app --host 0.0.0.0 --port 8091
```

Query via `curl`:

```bash
curl -s -X POST http://127.0.0.1:8091/kundli \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prithvi Raj",
    "dob": "2007-03-13",
    "tob": "18:05:00",
    "lat": 25.51095,
    "lon": 86.47246,
    "tz": 5.5
  }' | jq .ai_digest
```

---

## Testing & Verification

The test suite validates planetary math against the verified historical chart of M.K. Gandhi (2 Oct 1869, Porbandar) and asserts Sarvashtakavarga mathematical invariants (total sum = 337).

```bash
python3 tests/test_astro.py
```

---

## License

[MIT](LICENSE) © 2026 mwmQi
