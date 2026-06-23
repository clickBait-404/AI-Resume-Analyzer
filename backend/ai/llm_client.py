import json
import logging

from groq import Groq

from core.config import settings

logger = logging.getLogger(__name__)

_client: Groq | None = None


def _get_client() -> Groq | None:
    global _client

    if not settings.GROQ_API_KEY:
        return None

    if _client is None:
        _client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    return _client


def is_live() -> bool:
    return _get_client() is not None


def get_structured_completion(
    system_prompt: str,
    user_prompt: str
) -> dict | None:

    client = _get_client()

    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        system_prompt
                        + "\n\n"
                        + "Return ONLY valid JSON."
                        + " No markdown."
                        + " No explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.4,
        )

        content = response.choices[0].message.content

        return json.loads(content)

    except Exception:
        logger.exception(
            "Groq API call failed; falling back to mock response."
        )
        return None