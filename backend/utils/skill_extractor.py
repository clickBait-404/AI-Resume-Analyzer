"""
Rule-based skill extraction engine.

Given raw text, finds which canonical skills (from SKILL_TAXONOMY) are
present, using alias matching with word-boundary regex. This is fully
deterministic and explainable: for any match, you can point to the
exact alias and the exact position in the text that triggered it.

No ML. No embeddings. No similarity scores. Just precise pattern
matching against a curated taxonomy — which is exactly how most real
ATS keyword scanners work under the hood.
"""
import re

from utils.skill_taxonomy import SKILL_TAXONOMY

# Pre-compile one regex per alias for performance.
# Sort aliases longest-first so "node.js" matches before a hypothetical
# shorter overlapping alias would.
_COMPILED_PATTERNS: list[tuple[str, str, re.Pattern]] = []
for entry in SKILL_TAXONOMY:
    for alias in entry["aliases"]:
        # Escape regex special chars (e.g. "C++", "C#", ".NET") then
        # apply word-boundary-ish matching that still works for symbols.
        escaped = re.escape(alias.strip())
        pattern = re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)
        _COMPILED_PATTERNS.append((entry["canonical_name"], alias, pattern))

# Sort so longer aliases are tried first (avoids "C" matching inside "C++").
_COMPILED_PATTERNS.sort(key=lambda x: len(x[1]), reverse=True)


def extract_skills(text: str) -> list[str]:
    """
    Returns a sorted, de-duplicated list of canonical skill names found
    in the given text.
    """
    if not text:
        return []

    found: set[str] = set()
    for canonical_name, _alias, pattern in _COMPILED_PATTERNS:
        if pattern.search(text):
            found.add(canonical_name)

    return sorted(found)


def extract_skills_with_evidence(text: str) -> list[dict]:
    """
    Like extract_skills, but returns evidence for each match
    (which alias matched and at what character position) — used to
    make the scoring engine's explanations concrete and auditable.
    """
    results: dict[str, dict] = {}
    for canonical_name, alias, pattern in _COMPILED_PATTERNS:
        if canonical_name in results:
            continue
        match = pattern.search(text)
        if match:
            results[canonical_name] = {
                "skill": canonical_name,
                "matched_alias": alias,
                "position": match.start(),
            }

    return sorted(results.values(), key=lambda x: x["skill"])
