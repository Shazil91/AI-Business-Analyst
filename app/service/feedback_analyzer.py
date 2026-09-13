import json
import logging

from google import genai
from google.genai import types

from app.databases.models import FeedbackRating
from app.databases.memory import CompanyData
from app.core.gemini import API_KEY


logger = logging.getLogger(__name__)


class FeedbackAnalyzer:

    def __init__(self):
        if not API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=API_KEY
        )

        self.company_data = CompanyData()

    def analyze_email(
        self,
        subject: str | None,
        body: str,
    ) -> dict:

        if not body or not body.strip():
            raise ValueError(
                "Email body cannot be empty."
            )

        prompt = f"""
You are a customer feedback analysis system.

Analyze the following customer email.

Determine whether the email contains genuine
customer feedback about a product, service, experience,
problem, complaint, suggestion, or satisfaction.

Return ONLY valid JSON.

Required JSON structure:

{{
    "is_feedback": true,
    "rating": "very_bad | bad | neutral | good | very_good",
    "subject": "short description of the feedback",
    "comments": "concise summary of the customer's feedback"
}}

Rules:

- is_feedback must be true or false.
- If the email is not customer feedback:
  - is_feedback = false
  - rating = "neutral"
  - subject = ""
  - comments = ""
- Do not invent information.
- Use only information present in the email.
- "bad" should represent complaints, problems,
  dissatisfaction, or significant issues.
- "very_bad" should represent severe dissatisfaction
  or serious problems.
- "neutral" should represent neutral feedback.
- "good" should represent positive feedback.
- "very_good" should represent highly positive feedback.

Email subject:
{subject or ""}

Email body:
{body}
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        text = response.text.strip()

        try:
            result = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error(
                "Gemini returned invalid JSON: %s",
                text,
            )
            raise ValueError(
                "Gemini returned invalid feedback JSON."
            ) from exc

        return self._validate_result(result)

    @staticmethod
    def _validate_result(result: dict) -> dict:

        required_fields = {
            "is_feedback",
            "rating",
            "subject",
            "comments",
        }

        missing = required_fields - result.keys()

        if missing:
            raise ValueError(
                f"Feedback response missing fields: {missing}"
            )

        if not isinstance(
            result["is_feedback"],
            bool,
        ):
            raise ValueError(
                "is_feedback must be a boolean."
            )

        try:
            rating = FeedbackRating(
                result["rating"]
            )
        except ValueError as exc:
            raise ValueError(
                f"Invalid feedback rating: "
                f"{result['rating']}"
            ) from exc
        
        return {
            "is_feedback": result["is_feedback"],
            "rating": rating,
            "subject": (
                result["subject"] or ""
            ).strip(),
            "comments": (
                result["comments"] or ""
            ).strip(),
        }