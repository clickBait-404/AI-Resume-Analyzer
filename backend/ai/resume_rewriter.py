"""
AI Resume Rewriter.

Transforms weak resume bullets/summaries/project descriptions into
higher-impact statements. Uses OpenAI when configured; falls back to
a rule-based transformation (weak-verb substitution + structural
nudges) that is honest about its limits — it doesn't fabricate
content, it only restructures and strengthens phrasing.
"""
import re

from ai.llm_client import get_structured_completion, is_live
from ai.prompt_manager import RESUME_REWRITER_SYSTEM_PROMPT, build_resume_rewriter_user_prompt
from ai.response_validator import validate_resume_rewrite

# Weak opener -> stronger action verb suggestions. Deterministic,
# explainable substitution — not a generative rewrite. Each entry maps
# a regex matching the weak opener phrase to a replacement verb.
# The replacement always expects what follows to read naturally after
# it; phrases that don't fit grammatically are skipped rather than
# force-substituted (see _apply_verb_substitution).
WEAK_VERB_MAP = {
    r"^worked on\b": "Built",
    r"^helped (with|to)\b": "Contributed to",
    r"^responsible for\b": "Owned",
    r"^was responsible for\b": "Owned",
    r"^did\b": "Executed",
    r"^made\b": "Developed",
    r"^created\b": "Developed",
    r"^involved in\b": "Contributed to",
    r"^assisted (with|in)\b": "Supported",
    r"^used\b": "Leveraged",
    r"^in charge of\b": "Led",
}

WEAK_PHRASES = [
    "a web application",
    "various tasks",
    "different features",
    "some improvements",
]


def _apply_verb_substitution(text: str) -> tuple[str, bool]:
    """
    Returns (rewritten_text, was_changed). Only substitutes when the
    result reads grammatically — specifically, skips cases where the
    weak phrase is immediately followed by 'to <verb>' (e.g. "worked on
    the team TO BUILD apis"), since naive substitution there produces
    a broken double-verb sentence. Those are left for the AI path to
    handle properly; the mock fallback just leaves them unchanged
    rather than producing bad grammar.

    Also strips a redundant leading gerund right after the new verb
    (e.g. "Owned managing the database" -> "Owned the database"),
    since [strong verb] + [gerund] reads like two stacked verbs.
    """
    stripped = text.strip()
    for pattern, replacement in WEAK_VERB_MAP.items():
        match = re.match(pattern, stripped, flags=re.IGNORECASE)
        if not match:
            continue

        remainder = stripped[match.end():].lstrip()
        # Guard: if what follows still contains a second "to <verb>" or
        # "to <gerund>" construct close to the start, substitution is
        # likely to produce a grammatically broken sentence — skip.
        if re.match(r"^(the|a|an)\b.*\bto\s+\w+", remainder, flags=re.IGNORECASE):
            continue

        # If remainder starts with a gerund ("managing the database",
        # "improving the flow"), drop the gerund so [verb] + [gerund]
        # doesn't stack two actions awkwardly.
        gerund_match = re.match(r"^(\w+ing)\s+(.*)$", remainder, flags=re.IGNORECASE)
        if gerund_match:
            remainder = gerund_match.group(2)

        new_text = f"{replacement} {remainder}"
        new_text = new_text[0].upper() + new_text[1:] if new_text else new_text
        return new_text, True

    return text, False


def _build_mock_rewrite_single(original: str) -> dict:
    rewritten, verb_changed = _apply_verb_substitution(original)

    vague_terms_found = [p for p in WEAK_PHRASES if p in original.lower()]

    notes = []
    if verb_changed:
        notes.append("replaced a weak opening verb with a stronger action verb")
    if vague_terms_found:
        notes.append(f"flagged vague phrasing ('{vague_terms_found[0]}') that should be made more specific")
    if "%" not in original and not re.search(r"\d", original):
        notes.append("no quantifiable metric detected — consider adding one (e.g. scale, % improvement, time saved)")

    if not notes:
        improved = rewritten
        explanation = "No obvious weak patterns detected; consider adding a quantifiable outcome to strengthen this further."
    else:
        # Append a bracketed prompt for a metric rather than inventing one.
        if "no quantifiable metric detected" in " ".join(notes) and not rewritten.rstrip().endswith((".", "]")):
            improved = f"{rewritten.rstrip('.')}, improving [specific outcome — e.g. performance, reliability, or user experience]."
        else:
            improved = rewritten
        explanation = "; ".join(notes).capitalize() + "."

    return {
        "original": original,
        "improved": improved,
        "explanation": explanation,
    }


def _build_mock_rewrites(content_items: list[str]) -> dict:
    return {
        "rewrites": [_build_mock_rewrite_single(item) for item in content_items],
        "source": "mock_fallback",
    }


def rewrite_resume_content(content_items: list[str], jd_text: str | None = None) -> dict:
    """
    content_items: list of raw strings (summary, bullets, project
    descriptions) to improve. Returns {"rewrites": [...], "source": ...}
    """
    if not content_items:
        return {"rewrites": [], "source": "none"}

    if is_live():
        user_prompt = build_resume_rewriter_user_prompt(content_items, jd_text)
        result = get_structured_completion(RESUME_REWRITER_SYSTEM_PROMPT, user_prompt)
        if result and validate_resume_rewrite(result) and len(result["rewrites"]) == len(content_items):
            result["source"] = "openai"
            return result

    return _build_mock_rewrites(content_items)
