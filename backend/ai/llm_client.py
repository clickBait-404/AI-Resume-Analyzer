import json
import logging
import re
import time

import httpx
from groq import Groq

from core.config import settings

logger = logging.getLogger(__name__)

_client: Groq | None = None

# Matches ```json ... ``` or plain ``` ... ``` fences, possibly with
# leading/trailing whitespace around them.
_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)

# Network-level retry config. Groq calls can hit slow/flaky TLS
# handshakes (especially behind AV/proxy software on Windows); a
# couple of quick retries avoids falling back to the mock response
# for a single transient blip.
_MAX_RETRIES = 2
_RETRY_BACKOFF_SECONDS = 1.5
_REQUEST_TIMEOUT_SECONDS = 20.0


def _get_client() -> Groq | None:
    global _client

    if not settings.GROQ_API_KEY:
        return None

    if _client is None:
        _client = Groq(
            api_key=settings.GROQ_API_KEY,
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )

    return _client


def is_live() -> bool:
    return _get_client() is not None


def _clean_json_content(content: str) -> str:
    """
    Models frequently wrap JSON in markdown fences even when told not
    to. Strip those before parsing.
    """
    content = content.strip()

    match = _FENCE_RE.match(content)
    if match:
        content = match.group(1).strip()

    return content


def get_structured_completion(
    system_prompt: str,
    user_prompt: str
) -> dict | None:

    client = _get_client()

    if client is None:
        return None

    last_error: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 2):  # e.g. 1 initial + 2 retries
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
                response_format={"type": "json_object"},
            )

            choice = response.choices[0]
            content = choice.message.content

            if not content:
                logger.warning(
                    "Groq returned empty content. finish_reason=%r",
                    choice.finish_reason,
                )
                return None

            cleaned = _clean_json_content(content)

            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                logger.warning(
                    "Groq content was not valid JSON after cleaning. "
                    "Raw content (first 500 chars): %r",
                    content[:500],
                )
                return None

        except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
            last_error = exc
            logger.warning(
                "Groq network error on attempt %d/%d: %s",
                attempt,
                _MAX_RETRIES + 1,
                exc,
            )
            if attempt <= _MAX_RETRIES:
                time.sleep(_RETRY_BACKOFF_SECONDS * attempt)
                continue
            logger.error(
                "Groq unreachable after %d attempts. This is a network "
                "issue (not a code bug) - check antivirus SSL/HTTPS "
                "inspection, VPN, or firewall/proxy blocking "
                "api.groq.com.",
                _MAX_RETRIES + 1,
            )
            return None

        except Exception:
            logger.exception(
                "Groq API call failed; falling back to mock response."
            )
            return None

    if last_error:
        logger.error("Groq call ultimately failed: %s", last_error)
    return None