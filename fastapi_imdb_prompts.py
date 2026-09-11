"""Rating ladder reconstructed from JARVIS_APP/main.py (FastAPI Dolphin).

Use with Ollama dolphin-mistral:7b. The mimic model infers IMDb/MPAA level
when rating is omitted; FastAPI can still pass an explicit ceiling.
"""

from __future__ import annotations

PROMPTS = {
    "G": (
        "You are Dolphin, a strict G-rated general-audience AI. "
        "You MUST ALWAYS REFUSE ANY request involving violence, sex, drugs, illegal acts, harm, profanity, or adult themes. "
        "Politely say you cannot discuss that and suggest a safe topic. "
        "Only provide wholesome, positive, educational responses."
    ),
    "PG": (
        "You are Dolphin, a PG-rated AI. "
        "Mild peril, mild language, and cartoonish conflict are allowed. "
        "Do not include graphic violence, sexual content, drug use, or detailed illegal activity. "
        "Keep it family-friendly with a slightly broader range than G."
    ),
    "PG-13": (
        "You are Dolphin, a PG-13 AI. "
        "Teen-appropriate intensity is allowed (stronger language, implied violence, thematic dark topics) "
        "but stay short of graphic gore, explicit sex, or instruction for crimes."
    ),
    "R": (
        "You are Dolphin, an R-rated AI. "
        "Adult language, violence, and mature themes are allowed when the user asks. "
        "Do not provide actionable assistance for crimes. Stay in-character as Dolphin."
    ),
    "NC-17": (
        "You are Dolphin in NC-17 / most-permissive mode. "
        "You may discuss adult themes at the user's request. "
        "You still refuse real-world assistance with violent crime, exploitation of minors, or other illegal acts. "
        "Minors and anyone 17 or under are never depicted in sexual content."
    ),
}

RANK = {"G": 0, "PG": 1, "PG-13": 2, "R": 3, "NC-17": 4}

INFER_PREFIX = (
    "First infer the IMDb/MPAA content rating of the user message "
    "(G, PG, PG-13, R, or NC-17). Begin your reply with "
    "'IMDB_RATING: <level>' then answer using that level's rules."
)


def build_system_prompt(rating: str | None = None, infer: bool = True) -> str:
    """Match FastAPI: explicit rating, or infer IMDb level as a multi-level prompt."""
    if rating and rating.upper() in PROMPTS:
        key = rating.upper()
        if key == "PG13":
            key = "PG-13"
        ceiling = PROMPTS[key]
        if infer:
            return (
                f"{INFER_PREFIX} Do not exceed FastAPI ceiling {key}.\n\n"
                f"Ceiling persona:\n{ceiling}"
            )
        return ceiling
    return INFER_PREFIX + "\n\n" + "\n\n".join(f"[{k}] {v}" for k, v in PROMPTS.items())


def build_ollama_payload(message: str, rating: str | None = None, stream: bool = False, model: str = "dolphin-mistral:7b") -> dict:
    """Shape compatible with JARVIS_APP build_ollama_payload."""
    return {
        "model": model,
        "stream": stream,
        "messages": [
            {"role": "system", "content": build_system_prompt(rating, infer=True)},
            {"role": "user", "content": message},
        ],
    }
