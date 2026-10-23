"""data_astro.ai: Lossless full-fidelity payload delivery for AI ingestion."""

import json

ASTROLOGER_SYSTEM_PROMPT = """You are an expert Vedic Astrologer (Parashari + Jaimini).
You are provided the COMPLETE mathematical birth chart with 100% fidelity (no data omitted).
RULES:
1. Ground every statement strictly in the provided JSON data.
2. For every insight or prediction, cite exact coordinates: [Graha, House, Sign, Degree, Varga (D1-D60), Active Dasha].
3. Analyze D1 for physical foundation, D9 for marriage/inner potential, D10 for career/profession.
4. Walk the Vimshottari dasha hierarchy for precise event timing."""

def make_lossless_ai_payload(chart: dict, user_query: str = "Provide a comprehensive lifetime reading.") -> dict:
    """Delivers 100% complete astrological data to the LLM with zero data loss."""
    return {
        "messages": [
            {
                "role": "system",
                "content": ASTROLOGER_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"### COMPLETE VEDIC CHART DOSSIER (LOSSLESS)\n"
                    f"```json\n{json.dumps(chart, indent=2, ensure_ascii=False)}\n```\n\n"
                    f"### USER QUERY\n{user_query}"
                )
            }
        ]
    }
