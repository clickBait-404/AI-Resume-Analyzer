"""
Unit tests for the deterministic ATS scoring engine.
Run with: pytest tests/test_ats_scoring_engine.py
"""
from services.ats_scoring_engine import compute_skill_gap, run_ats_scoring


def _sample_parsed_resume(skills=None, experience=None, education=None):
    return {
        "contact_info": {"email": "a@b.com", "phone": "123-456-7890"},
        "skills": skills or [],
        "experience": experience or [],
        "education": education or [],
        "projects": [],
        "certifications": [],
    }


def _sample_parsed_jd(required=None, preferred=None, years=None):
    return {
        "required_skills": required or [],
        "preferred_skills": preferred or [],
        "responsibilities": [],
        "qualifications": [],
        "tools": [],
        "experience_required_years": years,
    }


def test_overall_score_is_weighted_average_of_subscores():
    parsed_resume = _sample_parsed_resume(
        skills=["Python", "FastAPI"],
        experience=[{"company": "X", "title": "Eng", "bullets": []}],
        education=[{"institution": "Y", "degree": "BS"}],
    )
    parsed_jd = _sample_parsed_jd(required=["Python", "FastAPI"], years=1)

    result = run_ats_scoring(parsed_resume, "Python FastAPI", parsed_jd, "Python FastAPI required")

    breakdown = result["score_breakdown"]
    expected = sum(c["score"] * c["weight"] for c in breakdown.values())
    assert abs(result["overall_score"] - round(expected, 1)) < 0.05


def test_full_skill_match_scores_100_on_skill_match_component():
    parsed_resume = _sample_parsed_resume(skills=["Python", "FastAPI", "PostgreSQL"])
    parsed_jd = _sample_parsed_jd(required=["Python", "FastAPI", "PostgreSQL"])

    result = run_ats_scoring(parsed_resume, "", parsed_jd, "")
    assert result["score_breakdown"]["skill_match"]["score"] == 100.0
    assert result["score_breakdown"]["skill_match"]["missing"] == []


def test_no_skill_match_scores_zero_on_skill_match_component():
    parsed_resume = _sample_parsed_resume(skills=["Java"])
    parsed_jd = _sample_parsed_jd(required=["Python", "FastAPI"])

    result = run_ats_scoring(parsed_resume, "", parsed_jd, "")
    assert result["score_breakdown"]["skill_match"]["score"] == 0.0
    assert set(result["score_breakdown"]["skill_match"]["missing"]) == {"Python", "FastAPI"}


def test_completeness_score_reflects_missing_sections():
    # Missing phone, skills, experience/projects, education -> only email present
    parsed_resume = {
        "contact_info": {"email": "a@b.com", "phone": None},
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
    }
    parsed_jd = _sample_parsed_jd()

    result = run_ats_scoring(parsed_resume, "", parsed_jd, "")
    # Only 1 of 5 checks passes (email present)
    assert result["score_breakdown"]["completeness"]["score"] == 20.0


def test_skill_gap_prioritizes_required_as_high_and_preferred_as_medium():
    gap = compute_skill_gap(
        resume_skills=["Python"],
        required_skills=["Python", "Django"],
        preferred_skills=["Kubernetes"],
    )
    priorities = {m["skill"]: m["priority"] for m in gap["missing_skills"]}
    assert priorities["Django"] == "High"
    assert priorities["Kubernetes"] == "Medium"
    assert gap["matched_skills"] == ["Python"]


def test_score_is_always_within_0_to_100_bounds():
    parsed_resume = _sample_parsed_resume(skills=["Python"] * 1)
    parsed_jd = _sample_parsed_jd(required=["Python"], preferred=["FastAPI", "Docker", "AWS", "PostgreSQL"])

    result = run_ats_scoring(parsed_resume, "", parsed_jd, "")
    assert 0.0 <= result["overall_score"] <= 100.0
    for component in result["score_breakdown"].values():
        assert 0.0 <= component["score"] <= 100.0
