"""
Rule-based job description analyzer.

Splits a pasted JD into responsibilities / qualifications, separates
required vs preferred skills using keyword cues ("required", "must
have" vs "nice to have", "preferred", "bonus"), and extracts a
required-years-of-experience number via regex. No ML.
"""
import re

from utils.skill_extractor import extract_skills

REQUIRED_CUES = re.compile(
    r"(required|requirements|must have|must-have|minimum qualifications|qualifications)",
    re.IGNORECASE,
)
PREFERRED_CUES = re.compile(
    r"(preferred|nice to have|nice-to-have|bonus|good to have|pluses?|desirable)",
    re.IGNORECASE,
)
RESPONSIBILITY_CUES = re.compile(
    r"(responsibilities|what you.?ll do|role overview|the role|duties|in this role)",
    re.IGNORECASE,
)
TOOLS_CUES = re.compile(r"(tools|technologies|tech stack)", re.IGNORECASE)
EXPERIENCE_YEARS_PATTERN = re.compile(r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?", re.IGNORECASE)


def _split_bulleted_lines(text: str) -> list[str]:
    lines = []
    for line in text.split("\n"):
        stripped = line.strip().lstrip("•-*▪◦").strip()
        if stripped and len(stripped) > 3:
            lines.append(stripped)
    return lines


def _find_section(text: str, cue_pattern: re.Pattern, all_cue_patterns: list[re.Pattern]) -> str:
    """
    Finds the block of text starting right after a line matching
    cue_pattern, up until the next line matching ANY other cue pattern
    (so sections don't bleed into each other).
    """
    lines = text.split("\n")
    start_idx = None
    for i, line in enumerate(lines):
        if cue_pattern.search(line) and len(line.strip()) < 80:
            start_idx = i + 1
            break

    if start_idx is None:
        return ""

    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        for other_pattern in all_cue_patterns:
            if other_pattern is cue_pattern:
                continue
            if other_pattern.search(lines[i]) and len(lines[i].strip()) < 80:
                end_idx = i
                break
        if end_idx != len(lines):
            break

    return "\n".join(lines[start_idx:end_idx])


def structure_job_description(raw_text: str) -> dict:
    """
    Main entry point: takes raw JD text and returns a structured dict
    matching the ParsedJobDescriptionData schema.
    """
    all_cues = [REQUIRED_CUES, PREFERRED_CUES, RESPONSIBILITY_CUES, TOOLS_CUES]

    required_section = _find_section(raw_text, REQUIRED_CUES, all_cues)
    preferred_section = _find_section(raw_text, PREFERRED_CUES, all_cues)
    responsibilities_section = _find_section(raw_text, RESPONSIBILITY_CUES, all_cues)
    tools_section = _find_section(raw_text, TOOLS_CUES, all_cues)

    # Skills mentioned in the "required" section (or whole doc if no
    # section was detected) count as required; skills only appearing
    # in the "preferred" section count as preferred.
    required_skills = extract_skills(required_section) if required_section else extract_skills(raw_text)
    preferred_skills = extract_skills(preferred_section) if preferred_section else []
    # Don't double-count: anything already required isn't also preferred.
    preferred_skills = [s for s in preferred_skills if s not in required_skills]

    tools = extract_skills(tools_section) if tools_section else []

    qualifications = _split_bulleted_lines(required_section) if required_section else []
    responsibilities = _split_bulleted_lines(responsibilities_section) if responsibilities_section else []

    years_match = EXPERIENCE_YEARS_PATTERN.search(raw_text)
    experience_required_years = int(years_match.group(1)) if years_match else None

    return {
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": responsibilities,
        "qualifications": qualifications,
        "tools": tools,
        "experience_required_years": experience_required_years,
    }
