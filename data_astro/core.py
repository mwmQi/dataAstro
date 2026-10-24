#!/usr/bin/env python3
"""
Vedic Kundli API — birth data in, full AI-ready chart JSON out.

    uvicorn kundli_api:app --host 0.0.0.0 --port 8091

POST /kundli  {"name":"John Doe", "dob":"1990-01-01", "tob":"12:00:00",
               "lat":25.51, "lon":86.47, "tz":5.5}
"""
import math
import datetime as dt
from typing import Optional

import swisseph as swe
from fastapi import FastAPI
from pydantic import BaseModel, Field

swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
_IMPORT_AYAN = swe.get_ayanamsa_ut(2454173.02431)

# ---------------------------------------------------------------- constants
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_SHORT = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
             "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

NAKS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
        "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
        "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
        "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
        "Revati"]
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
             "Saturn", "Mercury"] * 3

PLANETS = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
           ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
           ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
           ("Rahu", swe.MEAN_NODE)]

EXALT = {"Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165,
         "Jupiter": 95, "Venus": 357, "Saturn": 200}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
       "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10]}
MOOLTRIKONA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12),
               "Mercury": (5, 15, 20), "Jupiter": (8, 0, 10),
               "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
NAISARGIKA = {"Sun": 60, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
              "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57}
# natural friendship: planet -> (friends, enemies)
FRIENDS = {
    "Sun": (["Moon", "Mars", "Jupiter"], ["Venus", "Saturn"]),
    "Moon": (["Sun", "Mercury"], []),
    "Mars": (["Sun", "Moon", "Jupiter"], ["Mercury"]),
    "Mercury": (["Sun", "Venus"], ["Moon"]),
    "Jupiter": (["Sun", "Moon", "Mars"], ["Mercury", "Venus"]),
    "Venus": (["Mercury", "Saturn"], ["Sun", "Moon"]),
    "Saturn": (["Mercury", "Venus"], ["Sun", "Moon", "Mars"]),
    "Rahu": (["Venus", "Saturn", "Mercury"], ["Sun", "Moon", "Mars"]),
    "Ketu": (["Mars", "Venus", "Saturn"], ["Sun", "Moon"]),
}
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
               "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
               "Jupiter", "Saturn", "Mercury"]

TITHI = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
         "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
         "Trayodashi", "Chaturdashi", "Purnima/Amavasya"]
YOGA = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
        "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha",
        "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra",
        "Vaidhriti"]
KARANA = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
          "Shakuni", "Chatushpada", "Naga", "Kimstughna"]

app = FastAPI(title="Vedic Kundli API", version="1.0")


# ---------------------------------------------------------------- helpers
def dms(x: float) -> str:
    d = int(x)
    m = int((x - d) * 60)
    s = round(((x - d) * 60 - m) * 60)
    return f"{d}\u00b0{m:02d}'{s:02d}\""


def norm(x: float) -> float:
    return x % 360.0


def sign_of(lon: float) -> int:
    return int(norm(lon) // 30)


def deg_in_sign(lon: float) -> float:
    return norm(lon) % 30.0


def nak_of(lon: float) -> dict:
    span = 360.0 / 27
    idx = int(norm(lon) // span)
    within = norm(lon) - idx * span
    pada = int(within // (span / 4)) + 1
    return {"index": idx, "name": NAKS[idx], "lord": NAK_LORDS[idx],
            "pada": pada, "fraction_elapsed": within / span}


def dignity(planet: str, lon: float) -> str:
    s = sign_of(lon)
    if planet in EXALT:
        if s == sign_of(EXALT[planet]):
            return "Exalted (Uchcha)"
        if s == sign_of(EXALT[planet] + 180):
            return "Debilitated (Neecha)"
    if planet in MOOLTRIKONA:
        ms, lo, hi = MOOLTRIKONA[planet]
        if s == ms and lo <= deg_in_sign(lon) <= hi:
            return "Moolatrikona"
    if planet in OWN and s in OWN[planet]:
        return "Own sign (Swakshetra)"
    if planet in FRIENDS:
        fr, en = FRIENDS[planet]
        lord = SIGN_LORD[s]
        if lord == planet:
            return "Own sign"
        if lord in fr:
            return "Friendly sign"
        if lord in en:
            return "Enemy sign"
        return "Neutral sign"
    return "n/a"


def varga_sign(lon: float, n: int) -> int:
    """Divisional sign index for D-n."""
    sign = sign_of(lon)
    d = deg_in_sign(lon)
    if n == 1:
        return sign
    if n == 2:  # Hora
        odd = sign % 2 == 0
        return (4 if d < 15 else 3) if odd else (3 if d < 15 else 4)
    if n == 3:
        return (sign + int(d // 10) * 4) % 12
    if n == 4:
        return (sign + int(d // 7.5) * 3) % 12
    if n == 7:
        start = sign if sign % 2 == 0 else (sign + 6) % 12
        return (start + int(d // (30 / 7))) % 12
    if n == 9:
        part = int(d // (30 / 9))
        if sign % 3 == 0:
            start = sign
        elif sign % 3 == 1:
            start = (sign + 8) % 12
        else:
            start = (sign + 4) % 12
        return (start + part) % 12
    if n == 10:
        start = sign if sign % 2 == 0 else (sign + 8) % 12
        return (start + int(d // 3)) % 12
    if n == 12:
        return (sign + int(d // 2.5)) % 12
    if n == 16:
        start = [0, 4, 8][sign % 3]
        return (start + int(d // 1.875)) % 12
    if n == 20:
        start = [0, 8, 4][sign % 3]
        return (start + int(d // 1.5)) % 12
    if n == 24:
        start = 4 if sign % 2 == 0 else 3
        return (start + int(d // 1.25)) % 12
    if n == 27:
        start = [0, 3, 6, 9][sign % 4]
        return (start + int(d // (30 / 27))) % 12
    if n == 30:
        odd = sign % 2 == 0
        if odd:
            for lim, s in ((5, 0), (10, 10), (18, 8), (25, 2)):
                if d < lim:
                    return s
            return 6
        for lim, s in ((5, 1), (12, 5), (20, 11), (25, 9)):
            if d < lim:
                return s
        return 7
    if n == 40:
        start = 0 if sign % 2 == 0 else 6
        return (start + int(d // 0.75)) % 12
    if n == 45:
        start = [0, 4, 8][sign % 3]
        return (start + int(d // (30 / 45))) % 12
    if n == 60:
        return (sign + int(d * 2)) % 12
    raise ValueError(f"unsupported varga D{n}")


def varga_map(planet_lons: dict) -> dict:
    out = {}
    for n in (1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60):
        out[f"D{n}"] = {p: SIGN_SHORT[varga_sign(l, n)] for p, l in planet_lons.items()}
    return out


def house_of(lon: float, lagna_lon: float) -> int:
    """Whole-sign house 1..12."""
    return ((sign_of(lon) - sign_of(lagna_lon)) % 12) + 1


def karana_name(k: int) -> str:
    """k = int(elongation / 6), 0..59."""
    if k <= 0:
        return "Kimstughna"
    if k <= 56:
        return KARANA[(k - 1) % 7]
    return {57: "Shakuni", 58: "Chatushpada"}.get(k, "Naga")


def aspects(p: dict, hp: dict) -> list:
    """Graha drishti — Vedic sign-based aspects."""
    special = {"Mars": (4, 7, 8), "Jupiter": (5, 7, 9), "Saturn": (3, 7, 10),
               "Rahu": (5, 7, 9), "Ketu": (5, 7, 9)}
    out = []
    for name in [x[0] for x in PLANETS]:
        if name not in p:
            continue
        for h in special.get(name, (7,)):
            target = ((hp[name] - 1 + h - 1) % 12) + 1
            hit = [q for q in hp if q != name and hp.get(q) == target]
            out.append({"from": name, "aspect": f"{h}th", "to_house": target,
                        "planets_hit": hit})
    return out


def ai_digest(r: dict) -> str:
    """One compact paragraph an LLM can read before the raw JSON."""
    L, P = r["lagna"], r["planets"]
    d = r["dasha"]["current"]
    parts = [
        f'{r["birth"]["name"]} — born {r["birth"]["dob"]} {r["birth"]["tob"]} '
        f'(UTC{r["birth"]["tz"]:+g}), {r["birth"]["lat"]:.4f}N {r["birth"]["lon"]:.4f}E.',
        f'Lagna {L["sign"]} {L["degree_dms"]} ({L["nakshatra"]} pada {L["pada"]}), '
        f'lord {L["lord"]}.',
        f'Moon {P[1]["sign"]} {P[1]["degree_dms"]} in {P[1]["nakshatra"]} pada {P[1]["pada"]} '
        f'— {P[1]["nakshatra_lord"]} nakshatra.',
        "Grahas: " + "; ".join(
            f'{x["planet"]} {x["sign"]} {x["degree_dms"]} H{x["house"]}'
            f'{"" if x["dignity"] in ("Neutral sign", "") else " " + x["dignity"]}'
            f'{", R" if x["retrograde"] else ""}'
            for x in P),
        f'Dasha now: {d["lord"]} MD / {d["sub"]["lord"]} AD / {d["sub"]["sub"]["lord"]} PD '
        f'({d["sub"]["sub"]["start"][:10]} to {d["sub"]["sub"]["end"][:10]}).',
        f'Yogas: {", ".join(y["yoga"] for y in r["yogas"]) or "none detected"}.',
        f'Sade Sati: {"ACTIVE — " + str(r["sade_sati"]["active_phase"]) if r["sade_sati"]["is_active"] else "not active"}.',
        f'Sarvashtakavarga total {r["ashtakavarga"]["sarvashtakavarga_total"]} '
        f'(strongest signs: {", ".join(h for h, _ in sorted(r["ashtakavarga"]["sarvashtakavarga"].items(), key=lambda x: -x[1])[:3])}).',
    ]
    return " ".join(parts)


def jd_to_dt(jd: float) -> str:
    y, m, d, h = swe.revjul(jd)
    total = int(round(h * 3600))
    if total >= 86400:      # rounding carry into next day
        total -= 86400
        y, m, d = (dt.date(y, m, d) + dt.timedelta(days=1)).timetuple()[:3]
    hh, rem = divmod(total, 3600)
    mm, ss = divmod(rem, 60)
    return f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}"


# ---------------------------------------------------------------- dasha
def build_dasha(moon_lon: float, birth_jd: float, depth: int = 3) -> dict:
    nk = nak_of(moon_lon)
    lord = nk["lord"]
    total = DASHA_YEARS[lord]
    elapsed_years = nk["fraction_elapsed"] * total
    start_jd = birth_jd - elapsed_years * 365.2425

    seq = []
    i = DASHA_ORDER.index(lord)
    for k in range(9):
        seq.append(DASHA_ORDER[(i + k) % 9])

    def sub(lord_name, start, span_years, level, path):
        idx = DASHA_ORDER.index(lord_name)
        out = []
        cursor = start
        for k in range(9):
            sub_lord = DASHA_ORDER[(idx + k) % 9]
            yrs = span_years * DASHA_YEARS[sub_lord] / 120.0
            node = {
                "lord": sub_lord,
                "start": jd_to_dt(cursor),
                "end": jd_to_dt(cursor + yrs * 365.2425),
                "years": round(yrs, 4),
            }
            if level < depth:
                node["sub"] = sub(sub_lord, cursor, yrs, level + 1, path + [sub_lord])
            out.append(node)
            cursor += yrs * 365.2425
        return out

    tree = []
    cursor = start_jd
    for cycle in range(2):          # 2 cycles = 240 yrs, covers any living age
        for l in seq:
            yrs = DASHA_YEARS[l]
            node = {
                "lord": l, "start": jd_to_dt(cursor),
                "end": jd_to_dt(cursor + yrs * 365.2425), "years": yrs,
            }
            if depth >= 2:
                node["sub"] = sub(l, cursor, yrs, 2, [l])
            tree.append(node)
            cursor += yrs * 365.2425

    return {"balance_at_birth": {"lord": lord,
                                 "years": round(total - elapsed_years, 4)},
            "tree": tree}


def current_dasha(tree: list, now_jd: float) -> dict:
    def find(nodes):
        for n in nodes:
            s = swe.julday(*map(int, n["start"][:10].split("-")),
                           int(n["start"][11:13]) + int(n["start"][14:16]) / 60)
            e = swe.julday(*map(int, n["end"][:10].split("-")),
                           int(n["end"][11:13]) + int(n["end"][14:16]) / 60)
            if s <= now_jd < e:
                chain = {"lord": n["lord"], "start": n["start"], "end": n["end"]}
                if "sub" in n:
                    ch = find(n["sub"])
                    if ch:
                        chain["sub"] = ch
                return chain
        return None
    return find(tree) or {}


# ---------------------------------------------------------------- ashtakavarga
# Bindu contribution tables: for each planet, benefic houses counted from each
# of the 8 reference points (7 planets + Lagna). Totals per planet must equal
# the canonical 48/49/39/54/56/52/39 (= 337 Sarvashtakavarga).
AV = {
    "Sun": {"Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11], "Mercury": [3, 5, 6, 9, 10, 11, 12],
            "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "Lagna": [3, 4, 6, 10, 11, 12]},
    "Moon": {"Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11],
             "Mars": [2, 3, 5, 6, 9, 10, 11],
             "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
             "Jupiter": [1, 2, 4, 7, 8, 10, 11],
             "Venus": [3, 4, 5, 7, 9, 10, 11], "Saturn": [3, 5, 6, 11],
             "Lagna": [3, 6, 10, 11]},
    "Mars": {"Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11],
             "Mars": [1, 2, 4, 7, 8, 10, 11], "Mercury": [3, 5, 6, 11],
             "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
             "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11]},
    "Mercury": {"Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11],
                "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
                "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
                "Jupiter": [6, 8, 11, 12], "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
                "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
                "Lagna": [1, 2, 4, 6, 8, 10, 11]},
    "Jupiter": {"Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11],
                "Mars": [1, 2, 4, 7, 8, 10, 11],
                "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
                "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
                "Venus": [2, 5, 6, 9, 10, 11], "Saturn": [3, 5, 6, 12],
                "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]},
    "Venus": {"Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
              "Mars": [3, 5, 6, 9, 11, 12], "Mercury": [3, 5, 6, 9, 11],
              "Jupiter": [5, 8, 9, 10, 11],
              "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
              "Saturn": [3, 4, 5, 8, 9, 10, 11],
              "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]},
    "Saturn": {"Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11],
               "Mars": [3, 5, 6, 10, 11, 12], "Mercury": [6, 8, 9, 10, 11, 12],
               "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
               "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11]},
}
AV_TOTAL = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
            "Jupiter": 56, "Venus": 52, "Saturn": 39}


def ashtakavarga(sign_positions: dict) -> dict:
    """sign_positions: name -> sign index (0-11). Includes 'Lagna'."""
    bav = {}
    for planet, table in AV.items():
        row = [0] * 12
        for ref, houses in table.items():
            ref_sign = sign_positions[ref]
            for h in houses:
                row[(ref_sign + h - 1) % 12] += 1
        bav[planet] = row

    sav = [sum(bav[p][i] for p in bav) for i in range(12)]
    return {
        "bhinnashtakavarga": {p: dict(zip(SIGN_SHORT, v)) for p, v in bav.items()},
        "bhinnashtakavarga_totals": {p: sum(v) for p, v in bav.items()},
        "sarvashtakavarga": dict(zip(SIGN_SHORT, sav)),
        "sarvashtakavarga_total": sum(sav),
    }


# ---------------------------------------------------------------- shadbala
def shadbala(planets: dict, lagna_lon: float, sun_lon: float,
             moon_lon: float, jd: float, sunrise_jd: float,
             sunset_jd: float) -> dict:
    """Sthana / Dig / Kala / Naisargika / Cheshta. Drik bala omitted."""
    out = {}
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        lon = planets[name]["lon"]
        s = sign_of(lon)
        d = deg_in_sign(lon)

        # --- Sthana bala
        uchcha = 0.0
        if name in EXALT:
            dist = abs(((lon - EXALT[name] + 180) % 360) - 180)
            uchcha = dist / 3.0  # 60 virupas at max

        # saptavargaja (D1,D2,D3,D7,D9,D12,D30) dignity points
        sv = 0.0
        for n in (1, 2, 3, 7, 9, 12, 30):
            vs = varga_sign(lon, n)
            lord = SIGN_LORD[vs]
            if lord == name:
                sv += 45 if (n == 1 and vs in OWN.get(name, [])) else 30
            elif lord in FRIENDS.get(name, ([], []))[0]:
                sv += 15
            elif lord in FRIENDS.get(name, ([], []))[1]:
                sv += 3.75
            else:
                sv += 7.5

        # ojayugma: male planets in odd sign/rashi & odd navamsa
        male = name in ("Sun", "Mars", "Jupiter", "Mercury", "Saturn")
        oja = 0.0
        if male and s % 2 == 0:
            oja += 15
        if not male and s % 2 == 1:
            oja += 15
        if male and varga_sign(lon, 9) % 2 == 0:
            oja += 15
        if not male and varga_sign(lon, 9) % 2 == 1:
            oja += 15

        # kendradi: in kendra(1,4,7,10)=60, panaphara(2,5,8,11)=30, apoklima=15
        h = house_of(lon, lagna_lon)
        kendradi = 60.0 if h in (1, 4, 7, 10) else (30.0 if h in (2, 5, 8, 11) else 15.0)

        # drekkana: 1st third male signs, 2nd female, 3rd neutral
        drek = int(d // 10)
        drekkana = 15.0 if ((male and drek == 0) or (not male and drek == 1)) else 0.0

        sthana = uchcha + sv + oja + kendradi + drekkana

        # --- Dig bala: strongest in 10th/4th etc.
        ideal = {"Sun": 90, "Mars": 90, "Jupiter": 90, "Mercury": 90,
                 "Moon": 270, "Venus": 270, "Saturn": 270}[name]
        diff = abs(((lon - ideal + 180) % 360) - 180)
        dig = (180 - diff) / 3.0

        # --- Kala bala
        day_len = sunset_jd - sunrise_jd
        nathon = 0.0
        if day_len > 0:
            if sunrise_jd <= jd <= sunset_jd:
                frac = (jd - sunrise_jd) / day_len
            else:
                frac = ((jd - sunset_jd) % 1.0) / max(1e-9, 1 - day_len)
            noon = sunrise_jd + day_len / 2
            dist_hours = abs(jd - noon) * 24
            dist_hours = min(dist_hours, 24 - dist_hours)
            nathon = (12 - dist_hours) * 5  # 60 at noon for Moon, invert for Sun
            if name == "Sun":
                nathon = 60 - nathon
        paksha = 0.0
        elong = (moon_lon - sun_lon) % 360
        waxing = elong < 180
        benefic = name in ("Jupiter", "Venus") or (name == "Moon" and waxing)
        malefic = name in ("Sun", "Mars", "Saturn")
        if benefic and waxing:
            paksha = 60.0
        elif malefic and not waxing:
            paksha = 60.0
        elif benefic or malefic:
            paksha = 30.0
        else:
            paksha = 15.0

        tribhaga = 0.0
        if day_len > 0:
            third = (jd - sunrise_jd) / day_len
            lord_of_third = ["Mercury", "Sun", "Saturn"] if third < 1 else []
            if 0 <= third < 1 / 3 and name == "Mercury":
                tribhaga = 60.0
            elif 1 / 3 <= third < 2 / 3 and name == "Sun":
                tribhaga = 60.0
            elif 2 / 3 <= third <= 1 and name == "Saturn":
                tribhaga = 60.0

        ayan = abs(((lon - 90 + 180) % 360) - 180)  # crude ayana bala
        ayana = (23.45 - abs(23.45 - ayan / 15)) if ayan < 360 else 0
        ayana = max(0.0, min(60.0, 60 - abs(((lon % 360) - 90) % 360) / 3))

        kala = nathon + paksha + tribhaga + ayana

        # --- Cheshta (retrograde/speed based)
        speed = planets[name].get("speed", 0.0)
        if name in ("Sun", "Moon"):
            cheshta = 30.0
        elif speed < 0:
            cheshta = 60.0
        else:
            cheshta = max(0.0, 60 - abs(speed) * 20)

        nais = NAISARGIKA[name]

        out[name] = {
            "sthana_bala": round(sthana, 2),
            "dig_bala": round(dig, 2),
            "kala_bala": round(kala, 2),
            "cheshta_bala": round(cheshta, 2),
            "naisargika_bala": round(nais, 2),
            "total_virupas": round(sthana + dig + kala + cheshta + nais, 2),
            "total_rupas": round((sthana + dig + kala + cheshta + nais) / 60, 3),
            "note": "Drik bala not included; Kala bala is a partial (nathonnatha, "
                    "paksha, tribhaga, ayana).",
        }
    return out


# ---------------------------------------------------------------- yogas
def detect_yogas(p: dict, lagna_lon: float) -> list:
    y = []
    L = sign_of(lagna_lon)
    hp = {n: house_of(p[n]["lon"], lagna_lon) for n in p}

    # Panch Mahapurusha
    for name, yoga in [("Mars", "Ruchaka"), ("Mercury", "Bhadra"),
                       ("Jupiter", "Hamsa"), ("Venus", "Malavya"),
                       ("Saturn", "Sasa")]:
        dig = dignity(name, p[name]["lon"])
        if hp[name] in (1, 4, 7, 10) and ("Own" in dig or "Exalted" in dig
                                          or "Moolatrikona" in dig):
            y.append({"yoga": f"{yoga} Yoga", "planets": [name],
                      "basis": f"{name} in kendra (house {hp[name]}) — {dig}"})

    # Gajakesari: Jupiter in kendra from Moon
    jm = (sign_of(p["Jupiter"]["lon"]) - sign_of(p["Moon"]["lon"])) % 12 + 1
    if jm in (1, 4, 7, 10):
        y.append({"yoga": "Gajakesari Yoga", "planets": ["Jupiter", "Moon"],
                  "basis": f"Jupiter in {jm} from Moon (kendra)"})

    # Budhaditya
    if hp["Sun"] == hp["Mercury"]:
        y.append({"yoga": "Budhaditya Yoga", "planets": ["Sun", "Mercury"],
                  "basis": f"Sun+Mercury together in house {hp['Sun']}"})

    # Chandra-Mangala
    if hp["Moon"] == hp["Mars"]:
        y.append({"yoga": "Chandra-Mangala Yoga", "planets": ["Moon", "Mars"],
                  "basis": "Moon and Mars conjunct"})

    # Kemadruma (Moon isolated)
    moon_sign = sign_of(p["Moon"]["lon"])
    neighbours = {(moon_sign - 1) % 12, (moon_sign + 1) % 12}
    occupied = {sign_of(p[n]["lon"]) for n in p if n not in ("Moon",)}
    if not (neighbours & occupied) and hp["Moon"] not in (1,):
        y.append({"yoga": "Kemadruma Yoga", "planets": ["Moon"],
                  "basis": "No planet in 2nd/12th from Moon"})

    # Kendra Trikona Raja Yoga (lords of kendra & trikona conjunct/exchange)
    kendra_lords = {SIGN_LORD[(L + k) % 12] for k in (0, 3, 6, 9)}
    trikona_lords = {SIGN_LORD[(L + k) % 12] for k in (0, 4, 8)}
    for a in kendra_lords:
        for b in trikona_lords:
            if a != b and a in p and b in p and hp[a] == hp[b]:
                y.append({"yoga": "Raja Yoga (Kendra-Trikona)",
                          "planets": [a, b],
                          "basis": f"{a} and {b} conjunct in house {hp[a]}"})

    # Dhana yoga: 2nd/11th lords with 5th/9th lords
    dhana_lords = {SIGN_LORD[(L + 1) % 12], SIGN_LORD[(L + 10) % 12]}
    for a in dhana_lords:
        for b in trikona_lords:
            if a != b and a in p and b in p and hp[a] == hp[b]:
                y.append({"yoga": "Dhana Yoga", "planets": [a, b],
                          "basis": f"{a}+{b} in house {hp[a]}"})

    # Vipreet Raja Yoga: 6/8/12 lords in 6/8/12
    dust = {SIGN_LORD[(L + k) % 12] for k in (5, 7, 11)}
    for a in dust:
        if a in p and hp[a] in (6, 8, 12):
            y.append({"yoga": "Vipreet Raja Yoga", "planets": [a],
                      "basis": f"{a} (dusthana lord) placed in house {hp[a]}"})

    # Neecha Bhanga
    for name in p:
        if "Debilitated" in dignity(name, p[name]["lon"]):
            lord = SIGN_LORD[sign_of(p[name]["lon"])]
            if lord in p and hp[lord] in (1, 4, 7, 10):
                y.append({"yoga": "Neecha Bhanga Raja Yoga", "planets": [name, lord],
                          "basis": f"{name} debilitated, dispositor {lord} in kendra"})

    # Vargottama
    for name in p:
        if sign_of(p[name]["lon"]) == varga_sign(p[name]["lon"], 9):
            y.append({"yoga": "Vargottama", "planets": [name],
                      "basis": f"{name} in same sign in D1 and D9"})

    # Amala Yoga: Only natural benefics in 10th from Lagna or Moon
    tenth_from_lagna = [n for n in p if hp[n] == 10 and n in ("Jupiter", "Venus", "Mercury")]
    if tenth_from_lagna:
        y.append({"yoga": "Amala Yoga", "planets": tenth_from_lagna,
                  "basis": f"Natural benefic {', '.join(tenth_from_lagna)} in 10th house from Lagna"})

    # Parivartana Yoga (Mutual exchange of house lords)
    house_lords = {h: SIGN_LORD[(L + h - 1) % 12] for h in range(1, 13)}
    checked_exchanges = set()
    for h1 in range(1, 13):
        l1 = house_lords[h1]
        if l1 not in p: continue
        h2 = hp[l1]
        if h1 != h2:
            l2 = house_lords[h2]
            if l2 in p and hp[l2] == h1:
                pair = tuple(sorted([h1, h2]))
                if pair not in checked_exchanges:
                    checked_exchanges.add(pair)
                    y.append({"yoga": "Parivartana Yoga", "planets": [l1, l2],
                              "basis": f"Mutual exchange between House {h1} lord {l1} and House {h2} lord {l2}"})

    # Chandra-Shukra (Moon & Venus sambandha / 5-9 or kendra)
    mv = (sign_of(p["Venus"]["lon"]) - sign_of(p["Moon"]["lon"])) % 12 + 1
    if mv in (5, 9):
        y.append({"yoga": "Navapanchama Yoga (Moon-Venus)", "planets": ["Moon", "Venus"],
                  "basis": f"Moon and Venus in harmonious 5-9 relationship"})


    # Combustion
    for name in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Moon"):
        diff = abs(((p[name]["lon"] - p["Sun"]["lon"] + 180) % 360) - 180)
        limits = {"Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11,
                  "Venus": 10, "Saturn": 15}
        if diff < limits[name]:
            y.append({"yoga": "Combustion", "planets": [name],
                      "basis": f"{name} within {round(diff,2)}\u00b0 of Sun"})

    return y


# ---------------------------------------------------------------- karakas
def jaimini_karakas(p: dict) -> dict:
    """Chara karakas by degree within sign, descending."""
    order = sorted(((n, deg_in_sign(p[n]["lon"])) for n in
                    ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu")),
                   key=lambda x: -x[1])
    names = ["Atmakaraka (AK)", "Amatyakaraka (AmK)", "Bhratrikaraka (BK)",
             "Matrikaraka (MK)", "Putrakaraka (PK)", "Gnatikaraka (GK)",
             "Darakaraka (DK)"]
    out = {}
    for i, (planet, deg) in enumerate(order[:7]):
        out[names[i]] = {"planet": planet, "degree_in_sign": round(deg, 4)}
    return out


# ---------------------------------------------------------------- sade sati
def sade_sati(p: dict, now_jd: float) -> dict:
    moon_sign = sign_of(p["Moon"]["lon"])
    out = []
    for offset, phase in ((-1, "First (Rising)"), (0, "Second (Peak)"), (1, "Third (Setting)")):
        s = (moon_sign + offset) % 12
        # approximate Saturn transit window: Saturn takes ~2.46y per sign
        out.append({"phase": phase, "saturn_transit_sign": SIGNS[s]})
    sat_now, _ = swe.calc_ut(now_jd, swe.SATURN, FLAGS)
    sat_sign = sign_of(sat_now[0])
    active = None
    for offset, phase in ((-1, "First (Rising)"), (0, "Second (Peak)"), (1, "Third (Setting)")):
        if sat_sign == (moon_sign + offset) % 12:
            active = phase
    return {"moon_sign": SIGNS[moon_sign],
            "saturn_sign_now": SIGNS[sat_sign],
            "windows": out,
            "active_phase": active,
            "is_active": active is not None}


# ---------------------------------------------------------------- models
class Birth(BaseModel):
    name: str = "Unknown"
    dob: str = Field(..., description="YYYY-MM-DD")
    tob: str = Field(..., description="HH:MM:SS local time")
    lat: float
    lon: float
    tz: float = Field(5.5, description="UTC offset in hours, e.g. 5.5 for IST")
    dasha_depth: int = 3


@app.get("/debug")
def debug():
    return {"swe_file": swe.__file__, "mod_file": __file__,
            "sid_mode_default_ayan": swe.get_ayanamsa_ut(2454173.02431),
            "import_ayan": _IMPORT_AYAN}


@app.get("/health")
def health():
    return {"ok": True, "ephemeris": swe.version}


@app.post("/kundli")
def kundli(b: Birth) -> dict:
    # ponytail: re-set per call — swisseph's sid mode global does not carry into
    # uvicorn's threadpool workers, so a module-level set silently falls back to
    # Fagan/Bradley (~0.88 deg off). One line, correct in any thread.
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    y, m, d = (int(x) for x in b.dob.split("-"))
    hh, mm, ss = (int(x) for x in b.tob.split(":"))
    ut_hour = hh + mm / 60 + ss / 3600 - b.tz
    day_offset = 0
    while ut_hour < 0:
        ut_hour += 24
        day_offset -= 1
    while ut_hour >= 24:
        ut_hour -= 24
        day_offset += 1
    jd_ut = swe.julday(y, m, d + day_offset, ut_hour)

    # planets
    p = {}
    for name, code in PLANETS:
        xx, _ = swe.calc_ut(jd_ut, code, FLAGS)
        p[name] = {"lon": norm(xx[0]), "speed": xx[3]}
    p["Ketu"] = {"lon": norm(p["Rahu"]["lon"] + 180), "speed": p["Rahu"]["speed"]}

    # houses
    cusps, ascmc = swe.houses_ex(jd_ut, b.lat, b.lon, b'P', swe.FLG_SIDEREAL)
    lagna_lon = norm(ascmc[0])
    mc_lon = norm(ascmc[1])

    sun_lon = p["Sun"]["lon"]
    moon_lon = p["Moon"]["lon"]

    # planets block
    planets_out = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"):
        lon = p[name]["lon"]
        nk = nak_of(lon)
        planets_out.append({
            "planet": name,
            "sign": SIGNS[sign_of(lon)],
            "sign_short": SIGN_SHORT[sign_of(lon)],
            "degree_in_sign": round(deg_in_sign(lon), 6),
            "degree_dms": dms(deg_in_sign(lon)),
            "absolute_longitude": round(lon, 6),
            "nakshatra": nk["name"],
            "nakshatra_lord": nk["lord"],
            "pada": nk["pada"],
            "house": house_of(lon, lagna_lon),
            "dignity": dignity(name, lon),
            "retrograde": p[name].get("speed", 0) < 0 if name not in ("Rahu", "Ketu") else True,
            "speed_deg_per_day": round(p[name].get("speed", 0), 6),
            "navamsa_sign": SIGNS[varga_sign(lon, 9)],
            "vargottama": sign_of(lon) == varga_sign(lon, 9),
        })

    # panchang
    elong = (moon_lon - sun_lon) % 360
    tithi_num = int(elong // 12)
    paksha = "Shukla" if tithi_num < 15 else "Krishna"
    tithi_idx = tithi_num % 15
    yoga_num = int(((moon_lon + sun_lon) % 360) // (360 / 27))
    karana_num = int(elong // 6)
    weekday = (int(jd_ut + 1.5) % 7)
    WEEK = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    local_hours = (ut_hour + b.tz) % 24
    local_midnight_jd = jd_ut - local_hours / 24
    _rs, sunrise = swe.rise_trans(local_midnight_jd - 0.01, swe.SUN, swe.CALC_RISE,
                                  (b.lon, b.lat, 0))
    _ss, sunset = swe.rise_trans(local_midnight_jd - 0.01, swe.SUN, swe.CALC_SET,
                                 (b.lon, b.lat, 0))
    sunrise_jd = sunrise[0]
    sunset_jd = sunset[0]

    panchang = {
        "tithi_number": tithi_num + 1,
        "tithi": f"{paksha} {TITHI[tithi_idx]}",
        "paksha": paksha,
        "nakshatra": nak_of(moon_lon)["name"],
        "nakshatra_pada": nak_of(moon_lon)["pada"],
        "nakshatra_lord": nak_of(moon_lon)["lord"],
        "yoga": YOGA[yoga_num],
        "karana": karana_name(karana_num),
        "weekday": WEEK[weekday],
        "sunrise_local": jd_to_dt(sunrise_jd + b.tz / 24),
        "sunset_local": jd_to_dt(sunset_jd + b.tz / 24),
        "ayanamsa_lahiri": round(swe.get_ayanamsa_ut(jd_ut), 6),
        "julian_day_ut": round(jd_ut, 6),
    }

    # houses
    houses_out = {}
    for i in range(12):
        h = i + 1
        houses_out[f"H{h}"] = {
            "sign": SIGNS[(sign_of(lagna_lon) + i) % 12],
            "sign_lord": SIGN_LORD[(sign_of(lagna_lon) + i) % 12],
            "cusp_placidus_deg": round(norm(cusps[i]), 4),
            "cusp_placidus_dms": dms(norm(cusps[i])),
        }

    # varga
    all_lons = {n: p[n]["lon"] for n in p}
    all_lons["Lagna"] = lagna_lon

    # ashtakavarga
    sign_positions = {n: sign_of(l) for n, l in all_lons.items()}
    av = ashtakavarga(sign_positions)

    # dasha
    now_jd = swe.julday(*dt.datetime.utcnow().timetuple()[:3],
                        dt.datetime.utcnow().hour + dt.datetime.utcnow().minute / 60)
    dasha = build_dasha(moon_lon, jd_ut, b.dasha_depth)
    cur = current_dasha(dasha["tree"], now_jd)

    result = {
        "meta": {
            "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
            "ephemeris": f"Swiss Ephemeris {swe.version}",
            "ayanamsa": "Lahiri (Chitrapaksha)",
            "house_system": "Whole-sign bhavas + Placidus cusps (KP)",
        },
        "birth": {
            "name": b.name, "dob": b.dob, "tob": b.tob, "tz": b.tz,
            "lat": b.lat, "lon": b.lon,
            "utc_datetime": jd_to_dt(jd_ut),
        },
        "lagna": {
            "sign": SIGNS[sign_of(lagna_lon)],
            "degree_in_sign": round(deg_in_sign(lagna_lon), 6),
            "degree_dms": dms(deg_in_sign(lagna_lon)),
            "nakshatra": nak_of(lagna_lon)["name"],
            "pada": nak_of(lagna_lon)["pada"],
            "lord": SIGN_LORD[sign_of(lagna_lon)],
            "mc": SIGNS[sign_of(mc_lon)],
        },
        "panchang": panchang,
        "planets": planets_out,
        "houses": houses_out,
        "divisional_charts": varga_map(all_lons),
        "ashtakavarga": av,
        "shadbala": shadbala(p, lagna_lon, sun_lon, moon_lon, jd_ut,
                             sunrise_jd, sunset_jd),
        "dasha": {
            "system": "Vimshottari",
            "balance_at_birth": dasha["balance_at_birth"],
            "current": cur,
            "tree": dasha["tree"],
        },
        "yogas": detect_yogas(p, lagna_lon),
        "jaimini_karakas": jaimini_karakas(p),
        "sade_sati": sade_sati(p, now_jd),
        "transits_now": {
            name: {
                "sign": SIGNS[sign_of(swe.calc_ut(now_jd, code, FLAGS)[0][0])],
                "degree_dms": dms(deg_in_sign(swe.calc_ut(now_jd, code, FLAGS)[0][0])),
                "absolute_longitude": round(swe.calc_ut(now_jd, code, FLAGS)[0][0], 4),
            } for name, code in PLANETS
        },
        "aspects": aspects(p, {x["planet"]: x["house"] for x in planets_out}),
    }
    result["ai_digest"] = ai_digest(result)
    return result


if __name__ == "__main__":
    # self-check: varga math + ashtakavarga canonical totals
    assert varga_sign(0.0, 1) == 0
    assert varga_sign(10.0, 2) == 4      # Aries 1st half -> Leo (Sun's hora)
    assert varga_sign(20.0, 2) == 3      # Aries 2nd half -> Cancer
    assert varga_sign(40.0, 2) == 3      # Taurus 1st half -> Cancer
    assert varga_sign(0.0, 9) == 0       # Aries movable -> Aries
    assert varga_sign(30.0, 9) == 9      # Taurus fixed -> 9th from Ta = Capricorn
    assert varga_sign(60.0, 9) == 6      # Gemini dual -> 5th from Ge = Libra
    tot = {p: sum(len(h) for h in AV[p].values()) for p in AV}
    assert tot == AV_TOTAL, tot
    print("self-check ok", tot)
