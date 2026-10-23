# dataAstro

Deterministic, zero-scraping Vedic Astrology & AstroSage-compatible Kundli module built on **Swiss Ephemeris** (`pyswisseph`) with Lahiri / Chitrapaksha ayanamsa.

Given birth details (DOB, TOB, coordinates), computes the full astrological dossier without external API rate limits or subscriptions.

## Features

- **Panchang:** Tithi, Paksha, Nakshatra + Pada + Lord, Yoga, Karana, local Sunrise/Sunset.
- **Charts (16 Divisional Vargas):** D1 (Lagna), D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsha), D9 (Navamsha), D10 (Dashamsha / Career), D12, D16, D20, D24, D27, D30, D40, D45, D60 (Shashtiamsa).
- **Ashtakavarga:** Bhinnashtakavarga per graha + Sarvashtakavarga (asserted 337 constant).
- **Shadbala:** Sthana, Dig, Kala, Cheshta, Naisargika strengths in Virupas and Rupas.
- **Dasha Timeline:** Vimshottari dasha balance at birth, active MD / AD / PD lords, and full 240-year tree.
- **Yogas & Doshas:** Classical combinations (Budhaditya, Vipreet Raja Yoga, Vargottama) with mathematical proof basis.
- **Jaimini & Transits:** 7 Karakas (Atmakaraka..Darakaraka), Sade Sati phases, and real-time transit positions.
- **AI Digest:** Synthesized paragraph ready to prepend to LLM prompts for hallucination-free readings.

## Installation

```bash
pip install dataAstro
# or install from source
pip install -r requirements.txt
```

## Quickstart (Python API)

```python
from data_astro import get_person_details

chart = get_person_details(
    name="Prithvi Raj",
    dob="2007-03-13",
    tob="18:05:00",
    lat=25.51095,
    lon=86.47246,
    tz=5.5  # UTC+5.5 (IST)
)

print(chart["ai_digest"])
print("D10 Career 10th House:", chart["divisional_charts"]["D10"]["houses"]["10"])
```

## CLI Usage

```bash
python3 -m data_astro --name "Prithvi Raj" --dob 2007-03-13 --tob 18:05:00 --lat 25.51095 --lon 86.47246 --out chart.json
```

## Standalone REST API

```bash
uvicorn data_astro.core:app --host 0.0.0.0 --port 8091
# POST http://127.0.0.1:8091/kundli
```

## Testing

```bash
python3 tests/test_astro.py
```
