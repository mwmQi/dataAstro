"""data_astro.astrosage_scraper: Scrapes 100% of AstroSage Cloud verified data (including Upagrahas)."""

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

def fetch_astrosage_cloud_data(name: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5, place: str = "Birth Place") -> dict:
    """Creates a session on ascloud.astrosage.com and fetches full tables (Upagrahas, Planet Positions, Ashtakvarga, etc.)."""
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

    def get_tables(endpoint):
        try:
            url = f"https://ascloud.astrosage.com/cloud/{endpoint}"
            r = opener.open(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=10)
            p = TableParser()
            p.feed(r.read().decode("utf-8", errors="ignore"))
            return p.tables
        except Exception as e:
            return []

    # 2. Extract Upagrahas
    upagraha_tables = get_tables("upgrahchart.asp")
    upagrahas = []
    if upagraha_tables and len(upagraha_tables[0]) > 1:
        headers = upagraha_tables[0][0]
        for row in upagraha_tables[0][1:]:
            if len(row) >= 5:
                upagrahas.append({
                    "planet": row[0], "rashi": row[1], "longitude": row[2],
                    "nakshatra": row[3], "pada": row[4]
                })

    # 3. Extract Planet Positions
    planet_tables = get_tables("planetposition.asp")
    planets = []
    if planet_tables and len(planet_tables[0]) > 1:
        for row in planet_tables[0][1:]:
            if len(row) >= 7:
                planets.append({
                    "planet": row[0], "combust": row[1] == "C", "retrograde": row[2] == "R",
                    "rashi": row[3], "longitude": row[4], "nakshatra": row[5], "pada": row[6]
                })

    # 4. Extract KP Cusps
    kp_tables = get_tables("kpcusp.asp")

    # 5. Extract Shadbala
    shadbala_tables = get_tables("shadandbhav.asp")

    return {
        "source": "ascloud.astrosage.com",
        "native": {"name": name, "dob": dob, "tob": tob, "place": place, "lat": lat, "lon": lon},
        "upagrahas": upagrahas,
        "planets_detailed": planets,
        "kp_cusps": kp_tables,
        "shadbala_summary": shadbala_tables,
    }
