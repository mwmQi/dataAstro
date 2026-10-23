"""data_astro.astrosage_scraper: Scrapes 100% of AstroSage Cloud verified data (Upagrahas, Tables & Full Predictive Text Reports)."""

import urllib.request, urllib.parse, http.cookiejar, ssl, re, json
from html.parser import HTMLParser

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.curr_table = []
        self.curr_row = []
        self.curr_cell = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "table": self.curr_table = []
        elif tag == "tr": self.curr_row = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self.curr_cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_cell = False
            self.curr_row.append(" ".join("".join(self.curr_cell).split()))
        elif tag == "tr":
            if self.curr_row: self.curr_table.append(self.curr_row)
        elif tag == "table":
            if self.curr_table: self.tables.append(self.curr_table)

    def handle_data(self, data):
        if self.in_cell: self.curr_cell.append(data)

def extract_clean_text(html: str) -> list:
    """Extract clean content paragraphs from an HTML page."""
    clean = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
    lines = [l.strip() for l in re.sub(r"<[^>]+>", "\n", clean).splitlines() if l.strip()]
    return [l for l in lines if len(l) > 80 and not any(x in l.lower() for x in ["download now", "astrosage", "cookie policy", "terms of use"])]

def fetch_astrosage_cloud_data(name: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5, place: str = "Birth Place") -> dict:
    """Creates a session on ascloud.astrosage.com and fetches full tables + predictive reports."""
    y, m, d = dob.split("-")
    hh, mm, ss = (tob.split(":") + ["00", "00"])[:3]

    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    lat_abs = abs(lat)
    lon_abs = abs(lon)
    lat_deg = int(lat_abs)
    lat_min = int(round((lat_abs - lat_deg) * 60))
    lon_deg = int(lon_abs)
    lon_min = int(round((lon_abs - lon_deg) * 60))

    cj = http.cookiejar.CookieJar()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))

    form_data = {
        "name": name, "sex": "male", "day": str(int(d)), "month": str(int(m)), "year": str(int(y)),
        "hrs": str(int(hh)), "min": str(int(mm)), "sec": str(int(ss)), "place": place,
        "longdeg": str(lon_deg), "longmin": str(lon_min), "longew": lon_dir,
        "latdeg": str(lat_deg), "latmin": str(lat_min), "latns": lat_dir,
        "timezone": str(tz), "ayanamsa": "0", "charting": "0", "kphn": "0", "accuracy": ""
    }

    # 1. Create Session
    payload = urllib.parse.urlencode(form_data).encode("utf-8")
    req = urllib.request.Request(
        "https://ascloud.astrosage.com/cloud/createsession.asp",
        data=payload,
        headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"}
    )
    opener.open(req, timeout=12)

    def fetch_endpoint(endpoint):
        try:
            url = f"https://ascloud.astrosage.com/cloud/{endpoint}"
            r = opener.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=10)
            html = r.read().decode("utf-8", errors="ignore")
            p = TableParser()
            p.feed(html)
            text = extract_clean_text(html)
            return {"tables": p.tables, "text": text}
        except Exception:
            return {"tables": [], "text": []}

    # 2. Extract Upagrahas (Mandi, Gulika, Dhuma, Parivesha, etc.)
    upgrah_res = fetch_endpoint("upgrahchart.asp")
    upagrahas = []
    if upgrah_res["tables"] and len(upgrah_res["tables"][0]) > 1:
        for row in upgrah_res["tables"][0][1:]:
            if len(row) >= 5:
                upagrahas.append({
                    "planet": row[0], "rashi": row[1], "longitude": row[2],
                    "nakshatra": row[3], "pada": row[4]
                })

    # 3. Extract Detailed Planet & KP Tables
    planet_res = fetch_endpoint("planetposition.asp")
    planets = []
    if planet_res["tables"] and len(planet_res["tables"][0]) > 1:
        for row in planet_res["tables"][0][1:]:
            if len(row) >= 7:
                raw_name = row[0].split(" is in")[0].strip()
                planets.append({
                    "planet": raw_name, "combust": row[1] == "C", "retrograde": row[2] == "R",
                    "rashi": row[3], "longitude": row[4], "nakshatra": row[5], "pada": row[6]
                })

    kp_res = fetch_endpoint("kpcusp.asp")
    shadbala_res = fetch_endpoint("shadandbhav.asp")

    # 4. Extract Text Predictions (Ascendant, Lal Kitab, Dasha Phala, Sade Sati, Love)
    asc_pred = fetch_endpoint("ascendant-prediction.asp")["text"]
    lal_pred = fetch_endpoint("lalkitab-prediction.asp")["text"]
    sade_pred = fetch_endpoint("sadesatireport.asp")["text"]
    dasha_pred = fetch_endpoint("dasha_phala.asp")["text"]
    general_pred = fetch_endpoint("kundali-prediction.asp")["text"]
    love_pred = fetch_endpoint("love-horoscope.asp")["text"]

    return {
        "source": "ascloud.astrosage.com",
        "native": {"name": name, "dob": dob, "tob": tob, "place": place, "lat": lat, "lon": lon},
        "upagrahas": upagrahas,
        "planets_detailed": planets,
        "kp_cusps": kp_res["tables"],
        "shadbala_summary": shadbala_res["tables"],
        "predictions": {
            "ascendant_nature_health": asc_pred,
            "lal_kitab_predictions_and_upay": lal_pred,
            "sade_sati_lifecycle": sade_pred,
            "vimshottari_dasha_phala": dasha_pred,
            "general_life_trends": general_pred,
            "love_and_marriage": love_pred
        }
    }
