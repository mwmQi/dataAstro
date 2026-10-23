"""dataAstro: High-precision Vedic Astrology & AstroSage-compatible Kundli module."""

from .core import Birth, kundli, detect_yogas, ashtakavarga, build_dasha, shadbala
from .ai import make_lossless_ai_payload
from .astrosage_scraper import fetch_astrosage_cloud_data

def get_person_details(name: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5, include_astrosage_cloud: bool = False, place: str = "Birth Place") -> dict:
    """Calculate full Vedic profile and 16-varga astrological dossier."""
    b = Birth(name=name, dob=dob, tob=tob, lat=lat, lon=lon, tz=tz)
    data = kundli(b)
    if include_astrosage_cloud:
        cloud_data = fetch_astrosage_cloud_data(name, dob, tob, lat, lon, tz, place)
        data["astrosage_cloud"] = cloud_data
        data["upagrahas"] = cloud_data.get("upagrahas", [])
    return data

__all__ = ["get_person_details", "Birth", "kundli", "make_lossless_ai_payload", "fetch_astrosage_cloud_data"]
