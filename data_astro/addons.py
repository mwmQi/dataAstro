"""data_astro.addons: Lightweight, zero-bloat mathematical add-ons extracted from classical Jyotish (Arudha Padas & Ashta-Kuta Matchmaking)."""

# ------------------------------------------------------------- 1. Arudha Padas (A1..A12)
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
