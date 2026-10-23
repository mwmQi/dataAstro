# dataAstro

[![CI](https://github.com/mwmQi/dataAstro/actions/workflows/ci.yml/badge.svg)](https://github.com/mwmQi/dataAstro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Ephemeris: Swiss](https://img.shields.io/badge/Ephemeris-Swiss%20(Lahiri)-green.svg)](https://www.astro.com/swisseph/)

**dataAstro** is an enterprise-grade, deterministic Vedic Astrology calculation and Kundli extraction engine. Powered by Swiss Ephemeris (`pyswisseph`) and calibrated to standard **Lahiri (Chitrapaksha) Ayanamsa**, it delivers the full 59-point astrological ecosystem—covering all 16 Shodashvarga divisional charts (D1 to D60), Lal Kitab debts, Krishnamurti Paddhati (KP System), 6-fold Shadbala, 337-constant Ashtakavarga, Vimshottari Dasha trees, and LLM-ready synthesized digests.

Built as an open, zero-dependency calculation alternative to closed, rate-limited astrology platforms (AstroSage, Horocosmo).

---

## Architecture & Design Principles

1. **Pure Astronomy over Scraping:** All planetary longitudes, speeds, cusps, and divisional charts are calculated directly from NASA JPL / Swiss Ephemeris planetary models. No network latency, subscription walls, or fragile scraping pipelines.
2. **Mathematical Invariant Assertion:** Planetary strengths and tables are mathematically asserted against classical Jyotish constants (e.g. Sarvashtakavarga total = 337, 16-Varga mathematical sign boundaries).
3. **LLM Hallucination Guardrail:** Pre-synthesizes an `ai_digest` paragraph containing exact house occupants, active dasha chain, and dignity tokens. Feeding this digest into frontier models (Claude 3.5 Sonnet, GPT-4o, DeepSeek-R1) eliminates chart hallucination.

---

## Complete Feature Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                              dataAstro                                 │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ Core Astronomy     │ Divisional Vargas  │ Advanced Vedic Branches      │
├────────────────────┼────────────────────┼──────────────────────────────┤
│ • Lahiri Ayanamsa  │ • D1  (Lagna)      │ • Lal Kitab (Ghar & Debts)   │
│ • True Node / Rahu │ • D2  (Hora)       │ • KP System (Placidus Cusps) │
│ • Topocentric Moon │ • D3  (Drekkana)   │ • 6-fold Shadbala (Virupas)  │
│ • Local Panchang   │ • D4  (Chaturth)   │ • Ashtakavarga (337 Sum)     │
│ • Dignity Matrices │ • D7  (Saptamsha)  │ • Vimshottari 240-yr Tree    │
│ • Retrogression    │ • D9  (Navamsha)   │ • 15+ Classical Raja Yogas   │
│ • Combust & Varg.  │ • D10 (Dashamsha)  │ • Jaimini Karakas (AK..DK)   │
│ • Sunrise / Sunset │ • D12 to D60       │ • Sade Sati (3-phase check)  │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

### 1. Astronomical Panchang & Natal Basics
- **Tithi:** Exact paksha (Shukla/Krishna), tithi number, and exact ending moments.
- **Nakshatra:** 27 lunar mansions with 4 padas and sub-planetary rulers.
- **Yoga & Karana:** Classical 27 yogas (Vishkumbha to Vaidhriti) and 60 half-tithis (7 movable, 4 fixed).
- **Ascendant & Cusps:** Exact degree-minute-second (DMS) lagna with house sign lords.

### 2. Full Shodashvarga (16 Divisional Charts)
Computes all 16 classical Parashari vargas for domain-specific life analysis:
- **D1 (Rashi / Lagna):** Core body, health, vitality, self.
- **D2 (Hora):** Wealth, liquid assets, speech, financial destiny.
- **D3 (Drekkana):** Siblings, courage, motivation, short travels.
- **D4 (Chaturthamsa):** Real estate, vehicles, immovable property, inner fortune.
- **D7 (Saptamsha):** Children, progeny lineage, creative manifestations.
- **D9 (Navamsha):** Marriage, spouse nature, post-32 life evolution, inner soul.
- **D10 (Dashamsha):** Career, profession, executive authority, social status.
- **D12 (Dwadasamsha):** Parents, ancestry, inherited past karma.
- **D16 (Shodashamsha):** Conveyances, pleasures, vehicles, inner happiness.
- **D20 (Vimshamsha):** Spirituality, meditation, higher occult intuition.
- **D24 (Chaturvimshamsha):** Higher education, intellectual mastery, academic skills.
- **D27 (Saptavimshamsha):** Innate physical strengths, subconscious weaknesses.
- **D30 (Trimshamsha):** Karmic liabilities, misfortunes, chronic illnesses.
- **D40 (Khavedamsha):** General auspicious events and moral character.
- **D45 (Akshavedamsha):** Universal purity, holistic integrity, past karma.
- **D60 (Shashtiamsa):** Ultimate root karmic disposition (most critical micro-varga).
- **Specialized Lagnas:** Karakamsha (soul chart) and Swamsa charts.

### 3. Krishnamurti Paddhati (KP System)
- Placidus unequal house cusps calculated down to arcseconds.
- Planetary Star-Lord (Nakshatra ruler) and Sub-Lord hierarchy.
- House Cuspal Sub-Lords for event-timing verification.

### 4. Lal Kitab Matrix
- Natural Aries-first (Kalpurush) house conversions.
- Pakka Ghar (Permanent House placements of all 9 grahas).
- Planetary aspects, sleep states (Soya/Jaagta), and karmic debts (Pitra, Matru, Stri Rin).

### 5. Strength Systems (Shadbala & Ashtakavarga)
- **Shadbala:** Sthana Bala (positional), Dig Bala (directional), Kala Bala (temporal), Cheshta Bala (motional), Naisargika Bala (natural), and Drik Bala (aspectual) in Virupas and Rupas.
- **Ashtakavarga:** Individual Bhinnashtakavarga per planet + Sarvashtakavarga total benchmarked to the immutable 337 bindu invariant.

### 6. Life Timing (Vimshottari Dasha Tree)
- Birth balance calculated from Moon's nakshatra longitude.
- Multi-tier recursive tree: Mahadasha (MD) → Antardasha (AD) → Pratyantardasha (PD).
- 240-year multi-cycle coverage to prevent date overflow on elder natives.

---

## Installation

### Via Git / Pip (Recommended)

```bash
pip install git+https://github.com/mwmQi/dataAstro.git
```

### Local Development Setup

```bash
git clone https://github.com/mwmQi/dataAstro.git
cd dataAstro
pip install -r requirements.txt
pip install -e .
```

---

## Usage

### 1. Python API

```python
from data_astro import get_person_details

# Compute complete profile from raw birth coordinates
profile = get_person_details(
    name="Prithvi Raj",
    dob="2007-03-13",       # YYYY-MM-DD
    tob="18:05:00",          # HH:MM:SS (24-hr format)
    lat=25.51095,            # North decimal latitude
    lon=86.47246,            # East decimal longitude
    tz=5.5                   # UTC offset (IST = +5.5)
)

# 1. Synthesized AI Digest (for LLM prompt context)
print("Digest:\n", profile["ai_digest"])

# 2. Inspect Planetary Placements
for planet in profile["planets"]:
    print(f"{planet['planet']}: {planet['sign']} {planet['degree_dms']} in House {planet['house']} ({planet['dignity']})")

# 3. Query D10 Career Chart
d10 = profile["divisional_charts"]["D10"]
print("D10 10th House:", d10["houses"]["10"])

# 4. Check Current Dasha
current_dasha = profile["dasha"]["current"]
print(f"Active Dasha: {current_dasha['md']['lord']} MD / {current_dasha['ad']['lord']} AD / {current_dasha['pd']['lord']} PD")
```

### 2. Command Line Interface (CLI)

```bash
# Direct JSON extraction to stdout or file
python3 -m data_astro \
  --name "Prithvi Raj" \
  --dob "2007-03-13" \
  --tob "18:05:00" \
  --lat 25.51095 \
  --lon 86.47246 \
  --out prithvi_chart.json
```

### 3. Production REST API (FastAPI + Uvicorn)

Start the built-in microservice:

```bash
uvicorn data_astro.core:app --host 0.0.0.0 --port 8091
```

Query the API via `curl`:

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
  }' | jq '{ai_digest: .ai_digest, active_dasha: .dasha.current}'
```

---

## Verification & Golden Tests

The test suite asserts mathematical correctness against historical charts:
1. **M.K. Gandhi Chart (2 Oct 1869, 07:11:56 LMT, Porbandar):** Verifies sidereal lagna degrees, sign boundaries, and divisional mappings.
2. **Ashtakavarga Invariant:** Asserts total Sarvashtakavarga bindu sum across all 12 signs equals exactly 337.
3. **Ayanamsa Stability:** Re-asserts Lahiri sidereal mode in multi-threaded runtime environments.

Run the test suite:

```bash
python3 tests/test_astro.py
```

---

## Output Schema Summary

A successful call returns a structured ~88 KB payload:

| Key | Description |
|---|---|
| `ai_digest` | Concise synthesized text block designed for LLM prompts |
| `meta` | Ephemeris metadata, engine version, calculation timestamp |
| `birth` | Input parameters, local civil datetime, UTC datetime |
| `lagna` | Ascendant longitude, sign, nakshatra, pada, cusp degrees |
| `panchang` | Complete 5-fold astronomical calendar metrics |
| `planets` | Array of 9 grahas with degrees, houses, dignities, vargottama flags |
| `houses` | Whole-sign boundaries + KP Placidus cusp coordinates |
| `divisional_charts` | Full D1 through D60 divisional chart mappings |
| `ashtakavarga` | Bhinnashtakavarga matrices and Sarvashtakavarga scores |
| `shadbala` | Complete positional, directional, temporal, and motional scores |
| `dasha` | Multi-tier Vimshottari dasha hierarchy with start/end datetimes |
| `yogas` | Detected classical yogas with exact astrological criteria |
| `jaimini_karakas` | 7 Chara Karakas (Atmakaraka through Darakaraka) |
| `sade_sati` | Saturn transit phase analysis relative to natal Moon |

---

## License

Distributed under the [MIT License](LICENSE). Built by **mwmQi**.
