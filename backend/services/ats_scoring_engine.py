"""
ATS Scoring Engine.

Computes a transparent, deterministic 0-100 score for how well a
resume matches a job description, broken into five explainable
sub-scores. Every number here can be traced back to a concrete rule —
there is no black-box similarity metric.

Weights (sum to 1.0):
    Skill Match        40%
    Keyword Coverage    20%
    Experience Match    20%
    Education Match     10%
    Completeness         10%
"""
from utils.skill_extractor import extract_skills

WEIGHTS = {
    "skill_match": 0.40,
    "keyword_coverage": 0.20,
    "experience_match": 0.20,
    "education_match": 0.10,
    "completeness": 0.10,
}


def _score_skill_match(resume_skills: list[str], required_skills: list[str], preferred_skills: list[str]) -> dict:
    resume_skill_set = set(resume_skills)
    required_set = set(required_skills)
    preferred_set = set(preferred_skills)

    matched_required = resume_skill_set & required_set
    missing_required = required_set - resume_skill_set
    matched_preferred = resume_skill_set & preferred_set

    if not required_set:
        # No required skills detected in the JD — fall back to neutral score.
        score = 70.0
        explanation = "No clearly-labeled required skills were detected in the job description, so this score reflects general skill presence rather than a direct match."
    else:
        required_ratio = len(matched_required) / len(required_set)
        # Bonus for preferred skills, capped so it can't push score artificially high alone.
        preferred_bonus = min(len(matched_preferred) * 2, 10) if preferred_set else 0
        score = min(100.0, round(required_ratio * 100, 1) + preferred_bonus)
        explanation = (
            f"Matched {len(matched_required)} of {len(required_set)} required skills "
            f"({round(len(matched_required) / len(required_set) * 100)}%)"
            + (f", plus {len(matched_preferred)} preferred skill(s) as a bonus." if matched_preferred else ".")
        )

    return {
        "score": score,
        "weight": WEIGHTS["skill_match"],
        "explanation": explanation,
        "matched": sorted(matched_required | matched_preferred),
        "missing": sorted(missing_required),
    }


def _score_keyword_coverage(resume_text: str, jd_text: str) -> dict:
    """
    Distinct from skill match: this looks at ALL skills/keywords found
    in the JD (not just the 'required' section) and checks how many
    appear anywhere in the resume. Captures keyword density broadly,
    the way a real ATS keyword scanner would.
    """
    jd_keywords = set(extract_skills(jd_text))
    resume_keywords = set(extract_skills(resume_text))

    if not jd_keywords:
        return {
            "score": 70.0,
            "weight": WEIGHTS["keyword_coverage"],
            "explanation": "No identifiable keywords found in the job description to compare against.",
        }

    covered = jd_keywords & resume_keywords
    coverage_ratio = len(covered) / len(jd_keywords)
    score = round(coverage_ratio * 100, 1)

    return {
        "score": score,
        "weight": WEIGHTS["keyword_coverage"],
        "explanation": f"Resume contains {len(covered)} of {len(jd_keywords)} distinct keywords mentioned anywhere in the job description ({round(coverage_ratio * 100)}%).",
    }


def _score_experience_match(resume_experience: list[dict], required_years: int | None) -> dict:
    num_roles = len(resume_experience)

    if required_years is None:
        score = 75.0 if num_roles > 0 else 40.0
        explanation = (
            f"Job description did not specify a required years of experience. "
            f"Resume lists {num_roles} role(s)."
        )
        return {"score": score, "weight": WEIGHTS["experience_match"], "explanation": explanation}

    # Heuristic: assume each listed role represents roughly 1.5 years
    # on average when explicit dates aren't reliably parseable. This is
    # a coarse proxy, stated plainly rather than disguised as precision.
    estimated_years = num_roles * 1.5

    if estimated_years >= required_years:
        score = 100.0
        explanation = f"Resume shows approximately {estimated_years:.1f} estimated years of experience across {num_roles} role(s), meeting the {required_years}-year requirement."
    else:
        ratio = estimated_years / required_years if required_years > 0 else 0
        score = round(max(0, ratio) * 100, 1)
        explanation = f"Resume shows approximately {estimated_years:.1f} estimated years of experience across {num_roles} role(s), below the {required_years}-year requirement."

    return {"score": score, "weight": WEIGHTS["experience_match"], "explanation": explanation}


def _score_education_match(resume_education: list[dict]) -> dict:
    if not resume_education:
        return {
            "score": 30.0,
            "weight": WEIGHTS["education_match"],
            "explanation": "No education entries were detected on the resume.",
        }

    has_degree_info = any(e.get("degree") for e in resume_education)
    score = 90.0 if has_degree_info else 60.0
    explanation = (
        f"Detected {len(resume_education)} education entr{'y' if len(resume_education)==1 else 'ies'}"
        + (" with degree information." if has_degree_info else ", but degree details were unclear.")
    )

    return {"score": score, "weight": WEIGHTS["education_match"], "explanation": explanation}


def _score_completeness(parsed_resume: dict) -> dict:
    """
    Checks presence of the sections a resume needs to pass typical ATS
    parsing without errors: contact info, skills, experience or
    projects, and education.
    """
    contact = parsed_resume.get("contact_info", {})
    checks = {
        "Email present": bool(contact.get("email")),
        "Phone present": bool(contact.get("phone")),
        "Skills section present": bool(parsed_resume.get("skills")),
        "Experience or projects present": bool(parsed_resume.get("experience") or parsed_resume.get("projects")),
        "Education present": bool(parsed_resume.get("education")),
    }
    passed = sum(checks.values())
    total = len(checks)
    score = round((passed / total) * 100, 1)

    failed_checks = [name for name, ok in checks.items() if not ok]
    explanation = (
        f"{passed}/{total} completeness checks passed."
        + (f" Missing: {', '.join(failed_checks)}." if failed_checks else " All key sections present.")
    )

    return {"score": score, "weight": WEIGHTS["completeness"], "explanation": explanation}


def compute_skill_gap(resume_skills: list[str], required_skills: list[str], preferred_skills: list[str]) -> dict:
    resume_set = set(resume_skills)
    required_set = set(required_skills)
    preferred_set = set(preferred_skills)

    matched = sorted(resume_set & (required_set | preferred_set))

    missing_skills = []
    for skill in sorted(required_set - resume_set):
        missing_skills.append({"skill": skill, "priority": "High", "reason": "Listed as a required skill in the job description but not found on the resume."})
    for skill in sorted(preferred_set - resume_set):
        missing_skills.append({"skill": skill, "priority": "Medium", "reason": "Listed as a preferred skill in the job description but not found on the resume."})

    # Recommended: skills commonly paired with what's already required
    # that aren't explicitly in the JD — kept simple/deterministic by
    # just surfacing preferred skills not yet matched as "Low" priority
    # recommendations distinct from the missing list above isn't needed
    # here; recommended_skills covers adjacent high-value skills.
    recommended = sorted(preferred_set - resume_set - required_set)

    return {
        "matched_skills": matched,
        "missing_skills": missing_skills,
        "recommended_skills": recommended,
    }


def run_ats_scoring(parsed_resume: dict, resume_raw_text: str, parsed_jd: dict, jd_raw_text: str) -> dict:
    """
    Main entry point. Returns a dict matching the ScoreBreakdown +
    overall_score + skill_gap shape expected by the API layer.
    """
    resume_skills = parsed_resume.get("skills", [])
    required_skills = parsed_jd.get("required_skills", [])
    preferred_skills = parsed_jd.get("preferred_skills", [])

    skill_match = _score_skill_match(resume_skills, required_skills, preferred_skills)
    keyword_coverage = _score_keyword_coverage(resume_raw_text, jd_raw_text)
    experience_match = _score_experience_match(
        parsed_resume.get("experience", []), parsed_jd.get("experience_required_years")
    )
    education_match = _score_education_match(parsed_resume.get("education", []))
    completeness = _score_completeness(parsed_resume)

    breakdown = {
        "skill_match": skill_match,
        "keyword_coverage": keyword_coverage,
        "experience_match": experience_match,
        "education_match": education_match,
        "completeness": completeness,
    }

    overall_score = round(
        sum(component["score"] * component["weight"] for component in breakdown.values()),
        1,
    )

    skill_gap = compute_skill_gap(resume_skills, required_skills, preferred_skills)

    return {
        "overall_score": overall_score,
        "score_breakdown": breakdown,
        "skill_gap": skill_gap,
    }
