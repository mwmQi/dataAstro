"""data_astro.ui: 1:1 Pixel-perfect replica of modern dark-mode mobile Kundli screen."""

SIGN_NUMS = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4, "Leo": 5, "Virgo": 6,
    "Libra": 7, "Scorpio": 8, "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
}

PLANET_GLYPHS = {
    "Sun": "SU", "Moon": "MO", "Mars": "MA", "Mercury": "ME",
    "Jupiter": "JU", "Venus": "VE", "Saturn": "SA", "Rahu": "RA", "Ketu": "KE"
}

def render_reva_app_chart_svg(chart: dict) -> str:
    """Renders the exact dark square North-Indian chart from the mobile app."""
    lagna_sign = chart.get("lagna", {}).get("sign", "Libra")
    start_num = SIGN_NUMS.get(lagna_sign, 7)
    house_signs = {h: ((start_num + h - 2) % 12) + 1 for h in range(1, 13)}

    house_planets = {h: [] for h in range(1, 13)}
    for p in chart.get("planets", []):
        g = PLANET_GLYPHS.get(p["planet"], p["planet"][:2].upper())
        r_tag = "°" if p.get("retrograde") else ""
        house_planets[p["house"]].append(f"{g}{r_tag}")

    # Geometry for 360x360 app square
    coords = {
        1:  {"sign": (180, 145), "planets": (180, 95)},
        2:  {"sign": (110, 75),  "planets": (95, 45)},
        3:  {"sign": (75, 110),  "planets": (45, 95)},
        4:  {"sign": (145, 180), "planets": (95, 180)},
        5:  {"sign": (75, 250),  "planets": (45, 265)},
        6:  {"sign": (110, 285), "planets": (95, 315)},
        7:  {"sign": (180, 215), "planets": (180, 265)},
        8:  {"sign": (250, 285), "planets": (265, 315)},
        9:  {"sign": (285, 250), "planets": (315, 265)},
        10: {"sign": (215, 180), "planets": (265, 180)},
        11: {"sign": (285, 110), "planets": (315, 95)},
        12: {"sign": (250, 75),  "planets": (265, 45)},
    }

    lines = [
        '<svg viewBox="0 0 360 360" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background:#131313; border: 1.5px solid #2a2a2a; border-radius:16px;">',
        '  <rect x="12" y="12" width="336" height="336" fill="none" stroke="#333333" stroke-width="1.5"/>',
        '  <line x1="12" y1="12" x2="348" y2="348" stroke="#262626" stroke-width="1.5"/>',
        '  <line x1="348" y1="12" x2="12" y2="348" stroke="#262626" stroke-width="1.5"/>',
        '  <polygon points="180,12 348,180 180,348 12,180" fill="none" stroke="#333333" stroke-width="1.5"/>',
    ]

    for h in range(1, 13):
        sx, sy = coords[h]["sign"]
        px, py = coords[h]["planets"]
        s_num = house_signs[h]
        plist = "  ".join(house_planets[h])
        # Orange/brown small sign number
        lines.append(f'  <text x="{sx}" y="{sy}" fill="#a38260" font-size="11" font-weight="700" text-anchor="middle" font-family="-apple-system,sans-serif">{s_num}</text>')
        # Cream/white uppercase planet glyphs
        if plist:
            lines.append(f'  <text x="{px}" y="{py}" fill="#eaeaea" font-size="12" font-weight="700" text-anchor="middle" font-family="-apple-system,sans-serif">{plist}</text>')

    lines.append('</svg>')
    return "\n".join(lines)

def render_reva_screen_html(chart: dict) -> str:
    """Full 1:1 match to screenshot img_1efeedad7598.jpg."""
    b = chart["birth"]
    svg_chart = render_reva_app_chart_svg(chart)
    d, m, y = b["dob"].split("-")
    dob_short = f"{d}/{m}/{y[-2:]}"
    h, mn, _ = b["tob"].split(":")
    am_pm = "am" if int(h) < 12 else "pm"
    h12 = int(h) % 12 or 12
    tob_short = f"{h12:02d}:{mn}{am_pm}"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{b['name']} — Kundali</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #111111;
    color: #e5e5e5;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    justify-content: center;
    padding: 24px 12px;
  }}
  .app-frame {{
    width: 100%;
    max-width: 390px;
    background: #1a1917;
    border-radius: 32px;
    padding: 24px 18px;
    border: 1px solid #2a2825;
    box-shadow: 0 20px 50px rgba(0,0,0,0.8);
  }}
  .top-nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }}
  .user-header {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .user-name {{
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
  }}
  .edit-icon {{
    font-size: 14px;
    color: #a38260;
  }}
  .user-subline {{
    font-size: 13px;
    color: #8c8983;
    display: flex;
    gap: 8px;
    margin-bottom: 22px;
  }}
  .title-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .section-title {{
    font-size: 20px;
    font-weight: 700;
    color: #fff;
  }}
  .sun-moon-pill {{
    display: flex;
    gap: 12px;
    background: #24221f;
    border: 1px solid #33302b;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #d1cfc7;
  }}
  .chart-container {{
    width: 100%;
    aspect-ratio: 1;
    margin-bottom: 18px;
  }}
  .chart-selector {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #24221f;
    border: 1px solid #33302b;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    cursor: pointer;
    margin-bottom: 24px;
  }}
  .chevron {{ color: #a38260; }}
  .overview-card {{
    background: #24221f;
    border-radius: 16px;
    padding: 18px;
    border: 1px solid #33302b;
  }}
  .overview-card h4 {{ font-size: 15px; font-weight: 700; color: #fff; margin-bottom: 6px; }}
  .overview-card p {{ font-size: 13px; color: #a8a59d; line-height: 1.5; }}
</style>
</head>
<body>

<div class="app-frame">
  <div class="top-nav">
    <span style="font-size: 18px; color: #d1cfc7;">&larr;</span>
    <span style="font-size: 18px; color: #d1cfc7;">&#8942;</span>
  </div>

  <div class="user-header">
    <h2 class="user-name">{b['name']}</h2>
    <span class="edit-icon">&#9998;</span>
  </div>
  <div class="user-subline">
    <span>{dob_short}</span> &bull;
    <span>{tob_short}</span> &bull;
    <span>{b.get('place', 'Koderma')}</span>
  </div>

  <div class="title-row">
    <h3 class="section-title">Kundali</h3>
    <div class="sun-moon-pill">
      <span>&#9788; {chart['planets'][0]['sign']}</span>
      <span>&#9789; {chart['panchang']['nakshatra'].split()[0]}</span>
    </div>
  </div>

  <div style="font-size: 13px; color: #a38260; font-weight: 600; margin-bottom: 12px;">
    Lagna: {chart['lagna']['sign']} ({chart['lagna']['degree_dms'].split()[0]})
  </div>

  <div class="chart-container">
    {svg_chart}
  </div>

  <div class="chart-selector">
    <span>D1: Lagna</span>
    <span class="chevron">&#9662;</span>
  </div>

  <div class="overview-card">
    <h4>Life Overview</h4>
    <p>{chart['ai_digest']}</p>
  </div>
</div>

</body>
</html>
"""
