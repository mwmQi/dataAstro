"""dataAstro: High-precision Vedic Astrology & AstroSage-compatible Kundli module."""

from .core import Birth, kundli, detect_yogas, ashtakavarga, build_dasha, shadbala

def get_person_details(name: str, dob: str, tob: str, lat: float, lon: float, tz: float = 5.5) -> dict:
    """Calculate full Vedic profile and 16-varga astrological dossier."""
    b = Birth(name=name, dob=dob, tob=tob, lat=lat, lon=lon, tz=tz)
    return kundli(b)

__all__ = ["get_person_details", "Birth", "kundli"]
