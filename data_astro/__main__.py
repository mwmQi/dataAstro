#!/usr/bin/env python3
import sys, json, argparse
from . import get_person_details

def main():
    parser = argparse.ArgumentParser(description="dataAstro — Extract full person details and Vedic Kundli")
    parser.add_argument("--name", default="Native", help="Person name")
    parser.add_argument("--dob", required=True, help="Date of birth (YYYY-MM-DD)")
    parser.add_argument("--tob", required=True, help="Time of birth (HH:MM:SS)")
    parser.add_argument("--lat", type=float, required=True, help="Latitude (decimal degrees)")
    parser.add_argument("--lon", type=float, required=True, help="Longitude (decimal degrees)")
    parser.add_argument("--tz", type=float, default=5.5, help="UTC timezone offset (default: 5.5 for IST)")
    parser.add_argument("--place", default="Birth Place", help="Birth place string")
    parser.add_argument("--astrosage-cloud", action="store_true", help="Scrape live AstroSage Cloud (Upagrahas, Mandi, Gulika, etc.)")
    parser.add_argument("--html", help="Path to write responsive mobile card HTML preview")
    parser.add_argument("--svg", help="Path to write North-Indian diamond chart SVG")
    parser.add_argument("--out", help="Path to write full JSON chart")

    args = parser.parse_args()
    data = get_person_details(args.name, args.dob, args.tob, args.lat, args.lon, args.tz, include_astrosage_cloud=args.astrosage_cloud, place=args.place)

    if args.html:
        from .ui import generate_mobile_card_html
        with open(args.html, "w") as f:
            f.write(generate_mobile_card_html(data))
        print(f"✓ Mobile card HTML generated: {args.html}")

    if args.svg:
        from .ui import generate_north_kundli_svg
        with open(args.svg, "w") as f:
            f.write(generate_north_kundli_svg(data, "D1"))
        print(f"✓ North-Indian diamond SVG generated: {args.svg}")

    print("=== dataAstro AI Digest ===")
    print(data["ai_digest"])

    if args.out:
        with open(args.out, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nFull 88KB chart written to {args.out}")

if __name__ == "__main__":
    main()
