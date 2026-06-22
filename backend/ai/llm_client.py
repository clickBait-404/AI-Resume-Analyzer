"""
Thin wrapper around the OpenAI API. Centralizes:
  - client instantiation
  - structured JSON response handling
  - graceful fallback when no API key is configured

This is the ONLY module that should import the openai package —
everything else in ai/ talks to this client.
"""
import json
import logging

from openai import OpenAI

from core.config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI | None:
    global _client
    if not settings.OPENAI_API_KEY:
        return None
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def is_live() -> bool:
    """Whether real OpenAI calls will be made (vs mock fallback)."""
    return _get_client() is not None


def get_structured_completion(system_prompt: str, user_prompt: str) -> dict | None:
    """
    Calls the OpenAI API asking for a JSON object response.
    Returns None if no API key is configured (caller should use mock
    fallback) or if the call fails for any reason.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception:
        logger.exception("OpenAI API call failed; falling back to mock response.")
        return None
