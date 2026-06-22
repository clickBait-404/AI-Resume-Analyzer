"""
Recruiter Simulator.

Answers the questions a recruiter actually asks in the first-pass
screen: would I shortlist this candidate, what stands out, what
concerns me, what's missing, how competitive is this profile.

Uses OpenAI when configured. The mock fallback derives its verdict
from the real ATS score and skill gap rather than generic text, so
the decision (shortlist or not, confidence level) is at least
internally consistent with the rest of the analysis even without a
live model.
"""
from ai.llm_client import get_structured_completion, is_live
from ai.prompt_manager import RECRUITER_SIMULATOR_SYSTEM_PROMPT, build_recruiter_simulator_user_prompt
from ai.response_validator import validate_recruiter_simulation

# Score thresholds driving the mock verdict. Stated plainly rather
# than hidden — these are intentionally conservative cutoffs, not a
# claim about real recruiter behavior.
SHORTLIST_THRESHOLD = 65.0
HIGH_CONFIDENCE_MARGIN = 15.0


def _build_mock_simulation(parsed_resume: dict, skill_gap: dict, overall_score: float, score_breakdown: dict) -> dict:
    would_shortlist = overall_score >= SHORTLIST_THRESHOLD

    distance_from_threshold = abs(overall_score - SHORTLIST_THRESHOLD)
    if distance_from_threshold >= HIGH_CONFIDENCE_MARGIN:
        confidence = "High"
    elif distance_from_threshold >= HIGH_CONFIDENCE_MARGIN / 2:
        confidence = "Medium"
    else:
        confidence = "Low"

    matched = skill_gap.get("matched_skills", [])
    missing_high = [m["skill"] for m in skill_gap.get("missing_skills", []) if m["priority"] == "High"]

    standout_points = []
    if matched:
        standout_points.append(f"Hands-on experience with {', '.join(matched[:3])}, directly relevant to this role.")
    if parsed_resume.get("experience"):
        standout_points.append("Has real work experience listed, not just academic projects.")
    if score_breakdown.get("education_match", {}).get("score", 0) >= 80:
        standout_points.append("Education section is clear and complete.")
    if not standout_points:
        standout_points.append("Resume is at least parseable and structured cleanly.")

    concerns = []
    if missing_high:
        concerns.append(f"Missing core required skills: {', '.join(missing_high[:3])}.")
    if score_breakdown.get("experience_match", {}).get("score", 100) < 50:
        concerns.append("Experience level appears below what the role is asking for.")
    if score_breakdown.get("keyword_coverage", {}).get("score", 100) < 40:
        concerns.append("Low keyword overlap with the job description — may not even surface in an ATS keyword search.")
    if not concerns:
        concerns.append("No major red flags, but depth of experience in each listed skill isn't verifiable from the resume alone.")

    missing_elements = []
    if not parsed_resume.get("contact_info", {}).get("phone"):
        missing_elements.append("Phone number")
    if not parsed_resume.get("projects") and not parsed_resume.get("experience"):
        missing_elements.append("Any experience or project section at all")
    if not parsed_resume.get("certifications"):
        missing_elements.append("Certifications (not always required, but often a tiebreaker)")

    if overall_score >= 80:
        competitiveness = "This profile would likely rank in the top tier of applicants for this role based on skill and keyword alignment alone."
    elif overall_score >= 65:
        competitiveness = "This profile is competitive but not a standout — likely to make it past an initial screen, not guaranteed to be prioritized."
    elif overall_score >= 45:
        competitiveness = "This profile is below average competitiveness for this specific role; it would need a referral or a strong cover letter to get a second look."
    else:
        competitiveness = "This profile would likely be screened out at the resume stage for this specific role as written."

    verdict_summary = (
        f"{'Yes, I would shortlist this one.' if would_shortlist else 'No, I would pass on this one for this specific role.'} "
        f"Score of {overall_score}/100 against this JD, confidence: {confidence}."
    )

    return {
        "would_shortlist": would_shortlist,
        "shortlist_confidence": confidence,
        "standout_points": standout_points[:4],
        "concerns": concerns[:4],
        "missing_elements": missing_elements[:3],
        "competitiveness_assessment": competitiveness,
        "verdict_summary": verdict_summary,
        "source": "mock_fallback",
    }


def simulate_recruiter_review(
    resume_raw_text: str,
    jd_raw_text: str,
    parsed_resume: dict,
    skill_gap: dict,
    overall_score: float,
    score_breakdown: dict,
) -> dict:
    if is_live():
        user_prompt = build_recruiter_simulator_user_prompt(resume_raw_text, jd_raw_text, overall_score)
        result = get_structured_completion(RECRUITER_SIMULATOR_SYSTEM_PROMPT, user_prompt)
        if result and validate_recruiter_simulation(result):
            result["source"] = "openai"
            return result

    return _build_mock_simulation(parsed_resume, skill_gap, overall_score, score_breakdown)
