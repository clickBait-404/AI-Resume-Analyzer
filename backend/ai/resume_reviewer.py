"""
AI Resume Reviewer.

Generates recruiter-style feedback: strengths, weaknesses, missing
keywords, writing quality feedback, and ATS optimization suggestions.

Uses the OpenAI API when configured. Falls back to a deterministic,
data-driven mock response (built from the actual skill-gap analysis,
not generic placeholder text) when no API key is set — so the feature
is fully demoable without billing.

CHANGELOG:
- v2: pass matched_skills into the live prompt + reconciliation
  safety net, so the model can't contradict the deterministic engine
  (e.g. flagging "NoSQL" as missing when MongoDB/Redis are matched).
- v3: expanded CATEGORY_SYNONYMS (web protocols/architectures case)
  and added a first version of the unfalsifiable-requirement filter,
  keyed on literal words like "internal"/"proprietary".
- v4 (this version): the v3 unfalsifiable filter was too narrow — it
  missed "Lack of experience with RingCentral's specific technologies
  and systems," which doesn't use the word "internal" or "proprietary"
  at all, just a company-possessive construction. Replaced the fixed
  phrase list with a general heuristic pattern: "<CapitalizedWord>'s
  (specific/proprietary/internal )?(technology|tool|system|platform
  |product|stack)" — catches this class of phrasing without needing
  to know the company's name in advance. Documented false-negative
  risk below; this deliberately errs toward under-filtering rather
  than risking stripping legitimate feedback.
"""
import re

from ai.llm_client import get_structured_completion, is_live
from ai.prompt_manager import RESUME_REVIEWER_SYSTEM_PROMPT, build_resume_reviewer_user_prompt
from ai.response_validator import validate_resume_review


def _build_mock_review(parsed_resume: dict, skill_gap: dict, overall_score: float) -> dict:
    matched = skill_gap.get("matched_skills", [])
    missing = [m["skill"] for m in skill_gap.get("missing_skills", [])]
    high_priority_missing = [m["skill"] for m in skill_gap.get("missing_skills", []) if m["priority"] == "High"]

    strengths = []
    if matched:
        strengths.append(f"Demonstrates hands-on experience with {', '.join(matched[:4])}, which directly aligns with this role's requirements.")
    if parsed_resume.get("projects"):
        strengths.append(f"Includes {len(parsed_resume['projects'])} project(s), giving concrete evidence of applied skills rather than just claims.")
    if parsed_resume.get("experience"):
        strengths.append("Has listed work experience, which carries more weight with recruiters than projects alone.")
    if not strengths:
        strengths.append("Resume is parseable and contains identifiable structure (sections, contact info).")

    weaknesses = []
    if high_priority_missing:
        weaknesses.append(f"Missing several required skills for this role: {', '.join(high_priority_missing[:4])}.")
    if not parsed_resume.get("contact_info", {}).get("email"):
        weaknesses.append("No email address detected — this could cause an ATS to silently drop the application.")
    if overall_score < 60:
        weaknesses.append("Overall keyword and skill alignment with this job description is low; a recruiter skimming for 6-8 seconds is unlikely to see a strong match.")
    if not parsed_resume.get("experience") and not parsed_resume.get("projects"):
        weaknesses.append("No experience or project entries were detected — this is a significant gap for most technical roles.")
    if not weaknesses:
        weaknesses.append("No major structural weaknesses detected, though deeper quantification of impact (metrics, scale) would strengthen bullets further.")

    writing_quality_feedback = (
        "Resume structure is detectable and machine-readable, which is good for ATS parsing. "
        "Consider whether each bullet leads with a strong action verb and includes a measurable outcome."
    )

    ats_suggestions = []
    if missing:
        ats_suggestions.append(f"Work these missing keywords into your experience or skills section where genuinely applicable: {', '.join(missing[:5])}.")
    ats_suggestions.append("Use a standard single-column layout — tables and multi-column designs can break ATS text extraction.")
    ats_suggestions.append("Mirror exact terminology from the job description (e.g. if it says 'REST API', don't only write 'RESTful services').")
    ats_suggestions.append("Save and submit as .docx or text-based PDF, not an image-based or design-heavy PDF.")

    return {
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "missing_keywords": missing[:8],
        "writing_quality_feedback": writing_quality_feedback,
        "ats_optimization_suggestions": ats_suggestions[:5],
        "source": "mock_fallback",
    }


def generate_resume_review(
    resume_raw_text: str,
    jd_raw_text: str,
    parsed_resume: dict,
    skill_gap: dict,
    overall_score: float,
) -> dict:
    if is_live():
        matched_skills = skill_gap.get("matched_skills", [])
        user_prompt = build_resume_reviewer_user_prompt(
            resume_raw_text, jd_raw_text, overall_score, matched_skills
        )
        result = get_structured_completion(RESUME_REVIEWER_SYSTEM_PROMPT, user_prompt)
        if result and validate_resume_review(result):
            result = _reconcile_with_matched_skills(result, matched_skills)
            result = _strip_unfalsifiable_requirements(result)
            result["source"] = "openai"
            return result
        # Fall through to mock if the live call failed or returned bad data.

    return _build_mock_review(parsed_resume, skill_gap, overall_score)


# category keyword (lowercase, as it might appear in free text) ->
# specific skills that satisfy it if present in matched_skills.
#
# Honest limitation, unchanged from before: this is a small, curated
# map built from contradictions actually observed in practice, not a
# general-purpose skill ontology. Expect to keep adding entries.
CATEGORY_SYNONYMS: dict[str, set[str]] = {
    "nosql": {"mongodb", "redis", "cassandra", "dynamodb", "couchdb", "firebase"},
    "relational database": {"postgresql", "mysql", "sqlite", "oracle", "sql server"},
    "cloud": {"aws", "azure", "gcp", "google cloud"},
    "containerization": {"docker", "kubernetes"},
    "ci/cd": {"github actions", "jenkins", "gitlab ci", "circleci"},
    "version control": {"git", "github", "gitlab", "bitbucket"},
    "web protocol": {"rest api", "rest apis", "http", "https", "jwt", "graphql", "websocket", "websockets"},
    "web architecture": {"rest api", "rest apis", "http", "https", "graphql", "microservices", "openapi", "swagger"},
    "web format": {"rest api", "rest apis", "json", "openapi", "swagger", "graphql"},
    "api documentation": {"openapi", "swagger"},
}


def _reconcile_with_matched_skills(result: dict, matched_skills: list[str]) -> dict:
    """
    Belt-and-suspenders safety net on top of the prompt instruction.
    Strips any weakness, missing_keyword, or ATS suggestion that names
    a skill already confirmed as matched, OR names a category a
    matched skill already satisfies.
    """
    matched_lower = {s.lower() for s in matched_skills}

    def _text_is_satisfied_by_match(text: str) -> bool:
        text_lower = text.lower()
        if any(skill in text_lower for skill in matched_lower):
            return True
        for category, satisfying_skills in CATEGORY_SYNONYMS.items():
            if category in text_lower and satisfying_skills & matched_lower:
                return True
        return False

    result["weaknesses"] = [w for w in result.get("weaknesses", []) if not _text_is_satisfied_by_match(w)]
    result["missing_keywords"] = [
        k for k in result.get("missing_keywords", []) if not _text_is_satisfied_by_match(k)
    ]
    result["ats_optimization_suggestions"] = [
        s for s in result.get("ats_optimization_suggestions", []) if not _text_is_satisfied_by_match(s)
    ]

    if not result["weaknesses"]:
        result["weaknesses"] = [
            "No significant weaknesses identified relative to this role's confirmed skill matches."
        ]

    return result


# General heuristic pattern for "a company faulting the candidate for
# not already knowing its own proprietary tech" — WITHOUT needing to
# know the company's name in advance. Matches constructions like:
#   "RingCentral's specific technologies and systems"
#   "Google's proprietary systems"
#   "the company's internal platform"
# by looking for [CapitalizedWord]'s (or "the company's") followed by
# an optional qualifier (specific/proprietary/internal) and then a
# tech-related noun (technology, tool, system, platform, product,
# stack), directly adjacent — not separated by other words.
#
# Honest limitation: this deliberately requires the qualifier/noun to
# sit immediately after the possessive, to avoid false-positiving on
# ordinary phrases like "React's component model" or "Docker's
# container runtime." That means constructions with an extra word in
# between (e.g. "Salesforce's proprietary CRM platform") won't be
# caught. This errs toward under-filtering (a missed case slips
# through) rather than over-filtering (stripping legitimate feedback)
# — the system-prompt rule is the primary defense; this is a backstop
# for the clearest, most common phrasing only.
_UNFALSIFIABLE_PATTERNS = [
    re.compile(
        r"(?:[A-Z][A-Za-z&.]+(?:'s|\u2019s)|the company(?:'s|\u2019s))\s+"
        r"(?:specific\s+|proprietary\s+|internal\s+)?"
        r"(?:technolog(?:y|ies)|tools?|systems?|platforms?|products?|stack)\b",
        re.IGNORECASE,
    ),
    re.compile(r"internal (coding style|tools?|systems?|processes?|principles?)", re.IGNORECASE),
    re.compile(r"company['\u2019]s? (internal|proprietary)", re.IGNORECASE),
    re.compile(r"familiarity with (our|the company['\u2019]s?) (internal|proprietary)", re.IGNORECASE),
]


def _strip_unfalsifiable_requirements(result: dict) -> dict:
    """
    Removes weaknesses/missing_keywords that penalize the candidate
    for not already knowing something only learnable on the job.
    """
    def _is_unfalsifiable(text: str) -> bool:
        return any(pattern.search(text) for pattern in _UNFALSIFIABLE_PATTERNS)

    result["weaknesses"] = [w for w in result.get("weaknesses", []) if not _is_unfalsifiable(w)]
    result["missing_keywords"] = [k for k in result.get("missing_keywords", []) if not _is_unfalsifiable(k)]

    if not result["weaknesses"]:
        result["weaknesses"] = [
            "No significant weaknesses identified relative to this role's confirmed skill matches."
        ]

    return result