"""dataAstro: High-precision Vedic Astrology & AstroSage-compatible Kundli module."""

from .core import Birth, kundli, detect_yogas, ashtakavarga, build_dasha, shadbala
from .ai import make_lossless_ai_payload
from .astrosage_scraper import fetch_astrosage_cloud_data
from .ui import generate_north_kundli_svg, generate_mobile_card_html
from .addons import calculate_arudha_padas, calculate_36_guna_match, calculate_ishta_kashta_phala, calculate_12_month_transits

def get_person_details(name: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5, include_astrosage_cloud: bool = False, place: str = "Birth Place") -> dict:
    """Calculate full Vedic profile and 16-varga astrological dossier."""
    b = Birth(name=name, dob=dob, tob=tob, lat=lat, lon=lon, tz=tz)
    data = kundli(b)
    data["arudha_padas"] = calculate_arudha_padas(data)
    data["ishta_kashta_phala"] = calculate_ishta_kashta_phala(data)
    data["transits_12_months"] = calculate_12_month_transits(data, months=12)
    if include_astrosage_cloud:
        cloud_data = fetch_astrosage_cloud_data(name, dob, tob, lat, lon, tz, place)
        data["astrosage_cloud"] = cloud_data
        data["upagrahas"] = cloud_data.get("upagrahas", [])
        data["astrosage_predictions"] = cloud_data.get("predictions", {})
    return data

__all__ = [
    "get_person_details", "Birth", "kundli", "make_lossless_ai_payload",
    "fetch_astrosage_cloud_data", "generate_north_kundli_svg", "generate_mobile_card_html",
    "calculate_arudha_padas", "calculate_36_guna_match", "calculate_ishta_kashta_phala",
    "calculate_12_month_transits"
]
