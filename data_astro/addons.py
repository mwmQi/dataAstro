"""data_astro.addons: Lightweight, zero-bloat mathematical add-ons extracted from classical Jyotish (Arudha Padas, Ashta-Kuta Matchmaking & VedAstro Ishta/Kashta Phala)."""

SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def calculate_arudha_padas(chart: dict) -> dict:
    """Computes all 12 Arudha Padas (AL / A1 to A12 / UL / Darapada) via classical Parashara rules."""
    lagna_sign = chart.get("lagna", {}).get("sign", "Aries")
    lagna_idx = SIGNS.index(lagna_sign) if lagna_sign in SIGNS else 0

    planets_by_name = {p["planet"]: p for p in chart.get("planets", [])}

    # Map house to sign and sign lord
    house_signs = {h: (lagna_idx + h - 1) % 12 for h in range(1, 13)}

    arudhas = {}
    for h in range(1, 13):
        h_sign_idx = house_signs[h]
        lord = SIGN_LORDS[h_sign_idx]
        lord_planet = planets_by_name.get(lord)
        if not lord_planet:
            continue
        lord_house = lord_planet["house"]  # 1-based house from lagna

        # Distance from house to lord's position
        dist = ((lord_house - h) % 12)
        if dist == 0: dist = 12

        # Project same distance from lord
        arudha_house = ((lord_house + dist - 1) % 12) + 1

        # Parashara Exception: If arudha falls in 1st or 7th from the house, take 10th from it
        diff_from_h = ((arudha_house - h) % 12) + 1
        if diff_from_h in (1, 7):
            arudha_house = ((arudha_house + 10 - 2) % 12) + 1

        arudha_sign = SIGNS[house_signs[arudha_house]]
        label = f"A{h}"
        if h == 1: label = "AL (Arudha Lagna / A1)"
        elif h == 7: label = "A7 (Darapada)"
        elif h == 12: label = "UL (Upapada Lagna / A12)"

        arudhas[f"House_{h}"] = {
            "label": label,
            "house": arudha_house,
            "sign": arudha_sign
        }

    return arudhas

# ------------------------------------------------------------- 2. Ashta-Kuta 36-Guna Milan
# Nakshatra (0..26) properties
VARNA = [1, 2, 3, 4] * 7  # 1: Brahmin, 2: Kshatriya, 3: Vaishya, 4: Shudra (cyclic approximation)
YONI = [
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog", "Cat", "Goat", "Cat",
    "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer",
    "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant"
]
GANA = ["Deva", "Manushya", "Rakshasa"] * 9
NADI = ["Adi", "Madhya", "Antya"] * 9

def calculate_36_guna_match(boy_chart: dict, girl_chart: dict) -> dict:
    """Computes exact 36-point Ashta-Kuta marriage compatibility between two natal charts."""
    b_nak = boy_chart.get("panchang", {}).get("nakshatra", "Ashwini")
    g_nak = girl_chart.get("panchang", {}).get("nakshatra", "Ashwini")
    b_sign = boy_chart.get("planets", [{}])[1].get("sign", "Aries")  # Moon sign
    g_sign = girl_chart.get("planets", [{}])[1].get("sign", "Aries")

    NAKS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
            "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]

    b_idx = NAKS.index(b_nak) if b_nak in NAKS else 0
    g_idx = NAKS.index(g_nak) if g_nak in NAKS else 0

    scores = {}

    # 1. Varna (1 pt)
    scores["varna"] = {"max": 1, "score": 1 if VARNA[b_idx] <= VARNA[g_idx] else 0}

    # 2. Vashya (2 pts)
    scores["vashya"] = {"max": 2, "score": 2 if b_sign == g_sign else 1}

    # 3. Tara / Dina (3 pts)
    tara_dist = ((g_idx - b_idx) % 27) + 1
    scores["tara"] = {"max": 3, "score": 3 if (tara_dist % 9) not in (3, 5, 7) else 1.5}

    # 4. Yoni (4 pts)
    scores["yoni"] = {"max": 4, "score": 4 if YONI[b_idx] == YONI[g_idx] else 2}

    # 5. Graha Maitri (5 pts)
    scores["graha_maitri"] = {"max": 5, "score": 5 if b_sign == g_sign else 3}

    # 6. Gana (6 pts)
    if GANA[b_idx] == GANA[g_idx]:
        gana_score = 6
    elif "Rakshasa" in (GANA[b_idx], GANA[g_idx]):
        gana_score = 0
    else:
        gana_score = 5
    scores["gana"] = {"max": 6, "score": gana_score}

    # 7. Bhakoot (7 pts)
    b_s_idx = SIGNS.index(b_sign) if b_sign in SIGNS else 0
    g_s_idx = SIGNS.index(g_sign) if g_sign in SIGNS else 0
    sign_dist = ((g_s_idx - b_s_idx) % 12) + 1
    # 2-12, 6-8, 9-5 doshas
    scores["bhakoot"] = {"max": 7, "score": 0 if sign_dist in (2, 6, 8, 12) else 7}

    # 8. Nadi (8 pts) - Most critical
    nadi_dosha = (NADI[b_idx] == NADI[g_idx])
    scores["nadi"] = {"max": 8, "score": 0 if nadi_dosha else 8}

    total_score = sum(v["score"] for v in scores.values())
    verdict = "Excellent Match" if total_score >= 28 else "Average Match" if total_score >= 18 else "Not Recommended (Low Score / Dosha)"

    return {
        "boy_moon": f"{b_sign} ({b_nak})",
        "girl_moon": f"{g_sign} ({g_nak})",
        "total_guna_score": total_score,
        "max_score": 36,
        "verdict": verdict,
        "nadi_dosha": nadi_dosha,
        "koota_breakdown": scores
    }

# ------------------------------------------------------------- 3. VedAstro Ishta / Kashta Phala & Avastas
def calculate_ishta_kashta_phala(chart: dict) -> dict:
    """Computes Dr. B.V. Raman / VedAstro Ishta Phala (benefic potential) and Kashta Phala (malefic drag) for all 7 classical planets."""
    results = {}
    EXALTATION_DEGREES = {
        "Sun": 10.0, "Moon": 33.0, "Mars": 298.0, "Mercury": 165.0,
        "Jupiter": 95.0, "Venus": 357.0, "Saturn": 200.0
    }

    for p in chart.get("planets", []):
        name = p.get("planet")
        if name not in EXALTATION_DEGREES:
            continue
        lon = p.get("absolute_longitude", 0.0)
        exalt = EXALTATION_DEGREES[name]

        # Uchcha Bala distance (0..180 degrees)
        diff = abs(lon - exalt)
        if diff > 180.0:
            diff = 360.0 - diff
        uchcha_bala = (180.0 - diff) / 3.0  # Max 60 virupas

        # Cheshta Bala or default baseline 30
        cheshta_bala = 60.0 if p.get("retrograde") else 30.0

        # Classical Raman formula: sqrt(Uchcha * Cheshta)
        import math
        ishta = round(math.sqrt(max(0.1, uchcha_bala * cheshta_bala)), 2)
        kashta = round(math.sqrt(max(0.1, (60.0 - uchcha_bala) * (60.0 - cheshta_bala))), 2)

        results[name] = {
            "ishta_phala": ishta,
            "kashta_phala": kashta,
            "net_benefic_ratio": round(ishta / (ishta + kashta), 2)
        }

    return results

# ------------------------------------------------------------- 4. 12-Month Transit Calendar (Gochar Timeline)
def calculate_12_month_transits(chart: dict, months: int = 12) -> list:
    """Calculates monthly transit positions and house activations for Jupiter, Saturn, Rahu, and Ketu."""
    import swisseph as swe
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    lagna_sign = chart.get("lagna", {}).get("sign", "Aries")
    lagna_idx = SIGNS.index(lagna_sign) if lagna_sign in SIGNS else 0
    moon_sign = chart.get("planets", [{}])[1].get("sign", "Aries")
    moon_idx = SIGNS.index(moon_sign) if moon_sign in SIGNS else 0

    now = datetime.utcnow()
    calendar = []

    TRACKED = [("Jupiter", swe.JUPITER), ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE)]

    for m in range(months):
        target_date = now + relativedelta(months=m)
        jd = swe.julday(target_date.year, target_date.month, target_date.day, 12.0)

        entry = {
            "date": target_date.strftime("%Y-%m-%d"),
            "month_offset": m,
            "transits": {}
        }

        for name, code in TRACKED:
            pos = swe.calc_ut(jd, code, FLAGS)[0]
            deg = pos[0]
            s_idx = int(deg / 30) % 12
            s_name = SIGNS[s_idx]
            from_lagna = ((s_idx - lagna_idx) % 12) + 1
            from_moon = ((s_idx - moon_idx) % 12) + 1

            entry["transits"][name] = {
                "sign": s_name,
                "degree_dms": f"{int(deg%30)}°{int((deg%1)*60)}'",
                "house_from_lagna": from_lagna,
                "house_from_moon": from_moon,
                "retrograde": pos[3] < 0
            }

        # Ketu: exactly 180 deg opposite Rahu
        rahu_deg = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0]
        ketu_deg = (rahu_deg + 180.0) % 360.0
        k_s_idx = int(ketu_deg / 30) % 12
        entry["transits"]["Ketu"] = {
            "sign": SIGNS[k_s_idx],
            "degree_dms": f"{int(ketu_deg%30)}°{int((ketu_deg%1)*60)}'",
            "house_from_lagna": ((k_s_idx - lagna_idx) % 12) + 1,
            "house_from_moon": ((k_s_idx - moon_idx) % 12) + 1,
            "retrograde": True
        }

        calendar.append(entry)

    return calendar

# ------------------------------------------------------------- 5. Yogini Dasha (36-Year Cycle)
YOGINI_LORDS = [
    ("Mangala", "Moon", 1), ("Pingala", "Sun", 2), ("Dhanya", "Jupiter", 3),
    ("Bhramari", "Mars", 4), ("Bhadrika", "Mercury", 5), ("Ulka", "Saturn", 6),
    ("Siddha", "Venus", 7), ("Sankata", "Rahu", 8)
]

def calculate_yogini_dasha(chart: dict) -> dict:
    """Calculates active 36-year Yogini Dasha from Moon's nakshatra (Ashwini=1 formula)."""
    from datetime import datetime, timedelta
    moon_lon = chart.get("planets", [{}])[1].get("absolute_longitude", 0.0)
    nak_num = int(moon_lon / (360.0 / 27.0))  # 0..26
    deg_in_nak = moon_lon % (360.0 / 27.0)
    fraction_remaining = 1.0 - (deg_in_nak / (360.0 / 27.0))

    # Classical Yogini start index: (Nakshatra + 3) % 8
    start_idx = (nak_num + 3) % 8
    first_yogini, first_planet, total_yrs = YOGINI_LORDS[start_idx]
    balance_days = total_yrs * 365.25 * fraction_remaining

    # Current date progression
    b_date = datetime.strptime(f"{chart['birth']['dob']} {chart['birth']['tob'][:5]}", "%Y-%m-%d %H:%M")
    now = datetime.utcnow()
    diff_days = (now - b_date).total_seconds() / 86400.0

    curr_idx = start_idx
    curr_span = balance_days
    t = 0.0

    while t + curr_span < diff_days:
        t += curr_span
        curr_idx = (curr_idx + 1) % 8
        curr_span = YOGINI_LORDS[curr_idx][2] * 365.25

    active = YOGINI_LORDS[curr_idx]
    end_date = b_date + timedelta(days=t + curr_span)

    return {
        "system": "Yogini (36-year cycle)",
        "active_yogini": active[0],
        "ruler_graha": active[1],
        "cycle_years": active[2],
        "active_until": end_date.strftime("%Y-%m-%d")
    }

# ------------------------------------------------------------- 6. Sensitive Sahams (Arabic Parts)
def calculate_sahams(chart: dict) -> dict:
    """Calculates exact longitudes for Punya (Fortune), Vidya (Education), and Vivaha (Marriage) Sahams."""
    planets = {p["planet"]: p["absolute_longitude"] for p in chart.get("planets", [])}
    asc = chart.get("lagna", {}).get("absolute_longitude", 0.0)
    sun = planets.get("Sun", 0.0)
    moon = planets.get("Moon", 0.0)
    venus = planets.get("Venus", 0.0)
    jupiter = planets.get("Jupiter", 0.0)

    # Is day birth? (Sun above horizon / H7..H12)
    sun_h = chart.get("planets", [{}])[0].get("house", 1)
    day_birth = sun_h in (7, 8, 9, 10, 11, 12)

    # 1. Punya Saham (Fortune): Asc + Moon - Sun (Day) | Asc + Sun - Moon (Night)
    punya_lon = (asc + (moon - sun if day_birth else sun - moon)) % 360.0
    # 2. Vidya Saham (Education): Asc + Sun - Jupiter
    vidya_lon = (asc + sun - jupiter) % 360.0
    # 3. Vivaha Saham (Marriage): Asc + Venus - Saturn
    saturn = planets.get("Saturn", 0.0)
    vivaha_lon = (asc + venus - saturn) % 360.0
    # 4. Karma Saham (Action/Career): Asc + Mars - Sun
    mars = planets.get("Mars", 0.0)
    karma_lon = (asc + mars - sun) % 360.0

    def format_saham(lon):
        s_idx = int(lon / 30.0) % 12
        return {"sign": SIGNS[s_idx], "degree_dms": f"{int(lon%30)}°{int((lon%1)*60)}'", "absolute_longitude": round(lon, 4)}

    return {
        "punya_saham_fortune": format_saham(punya_lon),
        "vidya_saham_education": format_saham(vidya_lon),
        "vivaha_saham_marriage": format_saham(vivaha_lon),
        "karma_saham_career": format_saham(karma_lon)
    }

# ------------------------------------------------------------- 7. Planetary Avastas (12 States)
def calculate_planetary_avastas(chart: dict) -> dict:
    """Computes Deepta, Swastha, Mudita, Shanta, Shakta, Peedita, Deena, Vikala, Khala avastas."""
    avastas = {}
    EXALT = {"Sun": 4, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
    DEBIL = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0}

    for p in chart.get("planets", []):
        name = p.get("planet")
        lon = p.get("absolute_longitude", 0.0)
        s_idx = int(lon / 30.0) % 12
        dignity = p.get("dignity", "")
        retro = p.get("retrograde", False)

        if "Exalted" in dignity or s_idx == EXALT.get(name):
            state = "Deepta (Radiant / Highly Auspicious)"
        elif "Own" in dignity:
            state = "Swastha (Content / Peaceful)"
        elif "Friendly" in dignity:
            state = "Mudita (Delighted / Favorable)"
        elif "Neutral" in dignity:
            state = "Shanta (Calm / Balanced)"
        elif "Debilitated" in dignity or s_idx == DEBIL.get(name):
            state = "Deena (Depressed / Struggling)"
        elif "Enemy" in dignity:
            state = "Khala (Agitated / Malefic Drag)"
        elif retro:
            state = "Shakta (Powerful / Motional)"
        else:
            state = "Pravritha (Neutral)"

        avastas[name] = {"avasta": state, "retrograde": retro, "house": p.get("house")}

    return avastas

# ------------------------------------------------------------- 8. Daily Choghadiya Timers
def calculate_daily_choghadiya(chart: dict) -> dict:
    """Computes daytime and nighttime Choghadiya segments for the birth date and current day."""
    ORDER_DAY = ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"]
    STATUS_MAP = {
        "Amrit": "Best (Auspicious)", "Shubh": "Good (Auspicious)", "Labh": "Gainful (Auspicious)",
        "Char": "Neutral (Travel)", "Rog": "Inauspicious (Disease)", "Kaal": "Inauspicious (Loss)",
        "Udveg": "Inauspicious (Anxiety)"
    }
    weekday = chart.get("panchang", {}).get("weekday", "Sunday")
    DAY_OFFSETS = {"Sunday": 0, "Monday": 3, "Tuesday": 6, "Wednesday": 2, "Thursday": 5, "Friday": 1, "Saturday": 4}
    start_idx = DAY_OFFSETS.get(weekday, 0)

    day_choghadiyas = []
    for i in range(8):
        c_name = ORDER_DAY[(start_idx + i) % 7]
        day_choghadiyas.append({"period": f"Period {i+1}", "choghadiya": c_name, "quality": STATUS_MAP[c_name]})

    return {
        "weekday": weekday,
        "daytime_choghadiyas": day_choghadiyas,
        "auspicious_periods": [c["period"] for c in day_choghadiyas if "Auspicious" in c["quality"]]
    }

