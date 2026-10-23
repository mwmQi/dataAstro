"""data_astro.ui: Premium glassmorphic SVG & HTML chart generator."""

SIGN_NUMS = {
    "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4, "Leo": 5, "Virgo": 6,
    "Libra": 7, "Scorpio": 8, "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
}

PLANET_GLYPHS = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
}

def generate_north_kundli_svg(chart: dict, chart_type: str = "D1") -> str:
    """Generate a high-contrast diamond Vedic horoscope chart in clean SVG."""
    if chart_type == "D1":
        lagna_sign = chart.get("lagna", {}).get("sign", "Aries")
        planets_data = chart.get("planets", [])
        house_planets = {h: [] for h in range(1, 13)}
        for p in planets_data:
            house_planets[p["house"]].append(f"{PLANET_GLYPHS.get(p['planet'], p['planet'][:2])}{'(R)' if p.get('retrograde') else ''}")
    else:
        varga = chart.get("divisional_charts", {}).get(chart_type, {})
        lagna_sign = varga.get("Lagna", "Ar")
        # Map short to full
        short_map = {"Ar":"Aries","Ta":"Taurus","Ge":"Gemini","Cn":"Cancer","Le":"Leo","Vi":"Virgo","Li":"Libra","Sc":"Scorpio","Sg":"Sagittarius","Cp":"Capricorn","Aq":"Aquarius","Pi":"Pisces"}
        lagna_sign = short_map.get(lagna_sign, "Aries")
        lagna_num = SIGN_NUMS.get(lagna_sign, 1)
        house_planets = {h: [] for h in range(1, 13)}
        for p, s in varga.items():
            if p == "Lagna": continue
            p_sign = short_map.get(s, "Aries")
            p_num = SIGN_NUMS.get(p_sign, 1)
            h = ((p_num - lagna_num) % 12) + 1
            house_planets[h].append(PLANET_GLYPHS.get(p, p[:2]))

    start_num = SIGN_NUMS.get(lagna_sign, 1)
    house_signs = {h: ((start_num + h - 2) % 12) + 1 for h in range(1, 13)}

    # Positions for 12 houses inside a 400x400 diamond chart
    coords = {
        1:  {"sign": (200, 160), "planets": (200, 110)},
        2:  {"sign": (120, 80),  "planets": (110, 50)},
        3:  {"sign": (80, 120),  "planets": (50, 110)},
        4:  {"sign": (160, 200), "planets": (110, 200)},
        5:  {"sign": (80, 280),  "planets": (50, 290)},
        6:  {"sign": (120, 320), "planets": (110, 350)},
        7:  {"sign": (200, 240), "planets": (200, 290)},
        8:  {"sign": (280, 320), "planets": (290, 350)},
        9:  {"sign": (320, 280), "planets": (350, 290)},
        10: {"sign": (240, 200), "planets": (290, 200)},
        11: {"sign": (320, 120), "planets": (350, 110)},
        12: {"sign": (280, 80),  "planets": (290, 50)},
    }

    svg_lines = [
        '<svg viewBox="0 0 400 400" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="background:#0f172a; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">',
        '  <!-- Diamond Grid -->',
        '  <rect x="10" y="10" width="380" height="380" fill="none" stroke="#e2e8f0" stroke-width="2"/>',
        '  <line x1="10" y1="10" x2="390" y2="390" stroke="#94a3b8" stroke-width="1.5"/>',
        '  <line x1="390" y1="10" x2="10" y2="390" stroke="#94a3b8" stroke-width="1.5"/>',
        '  <polygon points="200,10 390,200 200,390 10,200" fill="none" stroke="#e2e8f0" stroke-width="2"/>',
    ]

    for h in range(1, 13):
        sx, sy = coords[h]["sign"]
        px, py = coords[h]["planets"]
        s_num = house_signs[h]
        plist = " ".join(house_planets[h])
        # Sign number (small orange)
        svg_lines.append(f'  <text x="{sx}" y="{sy}" fill="#fb923c" font-size="12" font-weight="bold" text-anchor="middle">{s_num}</text>')
        # Occupant Grahas (white bold)
        if plist:
            svg_lines.append(f'  <text x="{px}" y="{py}" fill="#f8fafc" font-size="13" font-weight="600" text-anchor="middle">{plist}</text>')

    svg_lines.append('</svg>')
    return "\n".join(svg_lines)

def generate_mobile_card_html(chart: dict) -> str:
    """Generate a clean dark-mode mobile card UI matching modern Astro apps."""
    b = chart["birth"]
    svg_d1 = generate_north_kundli_svg(chart, "D1")
    svg_d9 = generate_north_kundli_svg(chart, "D9")
    cur_d = chart["dasha"]["current"]

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{b['name']} — Kundli</title>
<style>
  * {{ box-sizing: border-box; margin:0; padding:0; }}
  body {{ background: #090d16; color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; justify-content: center; padding: 20px 10px; }}
  .mobile-card {{ width: 100%; max-width: 420px; background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .header h2 {{ font-size: 20px; font-weight: 700; color: #fff; }}
  .badge {{ background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.4); padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
  .sub-meta {{ font-size: 13px; color: #94a3b8; margin-bottom: 16px; }}
  .tab-bar {{ display: flex; gap: 8px; margin-bottom: 14px; }}
  .tab {{ padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid rgba(255,255,255,0.1); }}
  .tab.active {{ background: #f97316; color: #fff; border-color: #f97316; }}
  .chart-box {{ width: 100%; aspect-ratio: 1; margin-bottom: 16px; }}
  .info-strip {{ background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 12px; font-size: 13px; }}
  .info-row {{ display: flex; justify-content: space-between; margin-bottom: 6px; }}
  .info-row:last-child {{ margin-bottom: 0; }}
  .info-label {{ color: #94a3b8; }}
  .info-val {{ color: #f8fafc; font-weight: 600; }}
</style>
</head>
<body>
  <div class="mobile-card">
    <div class="header">
      <h2>{b['name']}</h2>
      <span class="badge">Lagna: {chart['lagna']['sign']}</span>
    </div>
    <div class="sub-meta">{b['dob']} • {b['tob']} • {chart['lagna']['degree_dms']}</div>

    <div class="tab-bar">
      <div class="tab active">D1: Lagna</div>
      <div class="tab">D9: Navamsha</div>
    </div>

    <div class="chart-box">
      {svg_d1}
    </div>

    <div class="info-strip">
      <div class="info-row">
        <span class="info-label">Moon / Nakshatra:</span>
        <span class="info-val">{chart['panchang']['nakshatra']} ({chart['panchang']['nakshatra_pada']})</span>
      </div>
      <div class="info-row">
        <span class="info-label">Tithi:</span>
        <span class="info-val">{chart['panchang']['tithi']}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Current Dasha:</span>
        <span class="info-val">{cur_d['lord']} MD / {cur_d['sub']['lord']} AD</span>
      </div>
      <div class="info-row">
        <span class="info-label">Sarvashtakavarga:</span>
        <span class="info-val">{sum(chart['ashtakavarga']['sarvashtakavarga'].values()) if isinstance(chart['ashtakavarga']['sarvashtakavarga'], dict) else 337} Bindus</span>
      </div>
    </div>
  </div>
</body>
</html>
"""
