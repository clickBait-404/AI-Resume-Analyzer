"""
Rule-based resume structuring engine.

Takes raw extracted text and splits it into sections (education,
experience, projects, certifications) using heading detection, then
extracts contact info via regex and skills via the skill extractor.

This is intentionally heuristic and transparent — every extraction
rule below is something you could explain to a human in one sentence.
No ML, no embeddings.
"""
import re

from utils.skill_extractor import extract_skills

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"(?<!\d)(\+\d{1,3}[\s.-]?)?(\(?\d{2,5}\)?[\s.-]?){2,4}\d{3,5}(?!\d)")
LINKEDIN_PATTERN = re.compile(r"(linkedin\.com/in/[A-Za-z0-9\-_/]+)", re.IGNORECASE)
GITHUB_PATTERN = re.compile(r"(github\.com/[A-Za-z0-9\-_/]+)", re.IGNORECASE)

# Section headings commonly found in resumes, mapped to our canonical section keys.
SECTION_HEADINGS = {
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "skills": ["skills", "technical skills", "core competencies", "skill set"],
}

DATE_RANGE_PATTERN = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|\d{4})"
    r"\s*[-–—to]+\s*"
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*\d{4}|\d{4}|[Pp]resent|[Cc]urrent)",
)


def _split_into_sections(text: str) -> dict[str, str]:
    """
    Splits raw resume text into named sections based on heading lines.
    A line is treated as a heading if it's short, and matches (loosely)
    one of our known heading keywords.
    """
    lines = text.split("\n")
    sections: dict[str, list[str]] = {}
    current_section = "header"  # everything before the first recognized heading
    sections[current_section] = []

    for line in lines:
        stripped = line.strip()
        normalized = stripped.lower().strip(":").strip()

        matched_section = None
        if 0 < len(normalized) <= 40:
            for section_key, keywords in SECTION_HEADINGS.items():
                if normalized in keywords or any(normalized == kw for kw in keywords):
                    matched_section = section_key
                    break

        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _extract_contact_info(text: str) -> dict:
    email_match = EMAIL_PATTERN.search(text)
    phone_match = PHONE_PATTERN.search(text)
    linkedin_match = LINKEDIN_PATTERN.search(text)
    github_match = GITHUB_PATTERN.search(text)

    # Name heuristic: first non-empty line that isn't an email/phone/url
    # and is short (resumes almost always start with the candidate's name).
    name = None
    for line in text.split("\n")[:5]:
        stripped = line.strip()
        if (
            stripped
            and len(stripped) < 60
            and "@" not in stripped
            and not PHONE_PATTERN.search(stripped)
            and "http" not in stripped.lower()
        ):
            name = stripped
            break

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "linkedin": linkedin_match.group(1) if linkedin_match else None,
        "github": github_match.group(1) if github_match else None,
        "location": None,  # left for future enhancement (geo-NER is out of scope for rule-based)
    }


def _extract_education(section_text: str) -> list[dict]:
    if not section_text:
        return []

    entries = []
    # Split on blank lines or lines that look like a new institution entry.
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section_text) if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        date_match = DATE_RANGE_PATTERN.search(block)
        gpa_match = re.search(r"GPA[:\s]*([\d.]+\s*/?\s*[\d.]*)", block, re.IGNORECASE)

        entries.append({
            "institution": lines[0] if lines else None,
            "degree": lines[1] if len(lines) > 1 else None,
            "field_of_study": None,
            "start_date": date_match.group(1) if date_match else None,
            "end_date": date_match.group(2) if date_match else None,
            "gpa": gpa_match.group(1).strip() if gpa_match else None,
        })
    return entries


def _extract_experience(section_text: str) -> list[dict]:
    if not section_text:
        return []

    entries = []
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section_text) if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        date_match = DATE_RANGE_PATTERN.search(block)
        bullets = [l.lstrip("•-*▪ ").strip() for l in lines if l.strip().startswith(("•", "-", "*", "▪"))]

        entries.append({
            "company": lines[0] if lines else None,
            "title": lines[1] if len(lines) > 1 else None,
            "start_date": date_match.group(1) if date_match else None,
            "end_date": date_match.group(2) if date_match else None,
            "bullets": bullets,
        })
    return entries


def _extract_projects(section_text: str) -> list[dict]:
    if not section_text:
        return []

    entries = []
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section_text) if b.strip()]
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        description = " ".join(lines[1:]) if len(lines) > 1 else ""
        technologies = extract_skills(block)

        entries.append({
            "name": lines[0] if lines else None,
            "description": description,
            "technologies": technologies,
        })
    return entries


def _extract_certifications(section_text: str) -> list[str]:
    if not section_text:
        return []
    lines = [l.lstrip("•-*▪ ").strip() for l in section_text.split("\n") if l.strip()]
    return lines


def structure_resume(raw_text: str) -> dict:
    """
    Main entry point: takes raw resume text and returns a structured
    dict matching the ParsedResumeData schema.
    """
    sections = _split_into_sections(raw_text)

    return {
        "contact_info": _extract_contact_info(raw_text),
        "education": _extract_education(sections.get("education", "")),
        "skills": extract_skills(sections.get("skills", "") or raw_text),
        "experience": _extract_experience(sections.get("experience", "")),
        "projects": _extract_projects(sections.get("projects", "")),
        "certifications": _extract_certifications(sections.get("certifications", "")),
    }
