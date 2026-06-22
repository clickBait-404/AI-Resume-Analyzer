"""
AI Resume Reviewer.

Generates recruiter-style feedback: strengths, weaknesses, missing
keywords, writing quality feedback, and ATS optimization suggestions.

Uses the OpenAI API when configured. Falls back to a deterministic,
data-driven mock response (built from the actual skill-gap analysis,
not generic placeholder text) when no API key is set — so the feature
is fully demoable without billing.
"""
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
        user_prompt = build_resume_reviewer_user_prompt(resume_raw_text, jd_raw_text, overall_score)
        result = get_structured_completion(RESUME_REVIEWER_SYSTEM_PROMPT, user_prompt)
        if result and validate_resume_review(result):
            result["source"] = "openai"
            return result
        # Fall through to mock if the live call failed or returned bad data.

    return _build_mock_review(parsed_resume, skill_gap, overall_score)
