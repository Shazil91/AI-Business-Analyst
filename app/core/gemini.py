import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


# ============================================================
# Configuration
# ============================================================

GEMINI_MODEL = "gemini-2.5-flash"

API_KEY = os.getenv("GEMINI_API_KEY")


if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add GEMINI_API_KEY to your .env file."
    )


# ============================================================
# Gemini Client
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# Gemini Helper
# ============================================================

def ask_gemini(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    """

    if not prompt or not prompt.strip():
        raise ValueError(
            "Gemini prompt cannot be empty."
        )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text