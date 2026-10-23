#!/usr/bin/env python3
"""Runnable checks for kundli_api. python3 test_kundli.py"""
from data_astro.core import Birth, kundli, varga_sign, AV, AV_TOTAL

# --- Ashtakavarga: canonical bindu totals per planet (must be exact) ---
tot = {p: sum(len(h) for h in AV[p].values()) for p in AV}
assert tot == AV_TOTAL, tot

# --- Varga boundary math ---
assert varga_sign(10.0, 2) == 4      # Aries 1st half -> Leo
assert varga_sign(20.0, 2) == 3      # Aries 2nd half -> Cancer
assert varga_sign(40.0, 2) == 3      # Taurus 1st half -> Cancer
assert varga_sign(30.0, 9) == 9      # Taurus (fixed) -> navamsa starts Capricorn
assert varga_sign(60.0, 9) == 6      # Gemini (dual) -> navamsa starts Libra

# --- Independent external check: M.K. Gandhi, 2 Oct 1869, 07:11:56 LMT, Porbandar.
# Published chart: Libra lagna, Sun Virgo, Moon Cancer, Mars Libra, Jupiter Aries,
# Venus Libra, Saturn Scorpio, Rahu Cancer.
r = kundli(Birth(name="MK Gandhi", dob="1869-10-02", tob="07:11:56",
                 lat=21.6417, lon=69.6293, tz=4.6419))
want = {"Sun": "Virgo", "Moon": "Cancer", "Mars": "Libra", "Mercury": "Libra",
        "Jupiter": "Aries", "Venus": "Libra", "Saturn": "Scorpio", "Rahu": "Cancer"}
got = {p["planet"]: p["sign"] for p in r["planets"]}
assert r["lagna"]["sign"] == "Libra", r["lagna"]["sign"]
for k, v in want.items():
    assert got[k] == v, (k, got[k], v)

# --- Structural invariants ---
assert len(r["planets"]) == 9
assert len(r["divisional_charts"]) == 16
assert r["ashtakavarga"]["sarvashtakavarga_total"] == 337
assert 21 < r["panchang"]["ayanamsa_lahiri"] < 23   # Lahiri c.1869
assert sum(h["years"] for h in r["dasha"]["tree"][:9]) == 120
assert r["dasha"]["current"] is not None
for h in r["planets"]:
    assert 0 <= h["degree_in_sign"] < 30
    assert 1 <= h["pada"] <= 4
    assert 1 <= h["house"] <= 12

print("all checks passed")
