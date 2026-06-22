"""
Unit tests for the recruiter simulator mock fallback.
Run with: pytest tests/test_recruiter_simulator.py
"""
from ai.recruiter_simulator import SHORTLIST_THRESHOLD, _build_mock_simulation


def _sample_resume(has_phone=True, has_experience=True):
    return {
        "contact_info": {"email": "a@b.com", "phone": "123-456-7890" if has_phone else None},
        "experience": [{"company": "X"}] if has_experience else [],
        "projects": [],
        "certifications": [],
    }


def _sample_skill_gap(missing_high=None):
    return {
        "matched_skills": ["Python", "FastAPI"],
        "missing_skills": [{"skill": s, "priority": "High", "reason": "r"} for s in (missing_high or [])],
    }


def _sample_breakdown(experience_score=80, keyword_score=80, education_score=80):
    return {
        "education_match": {"score": education_score},
        "experience_match": {"score": experience_score},
        "keyword_coverage": {"score": keyword_score},
    }


def test_score_above_threshold_shortlists():
    result = _build_mock_simulation(_sample_resume(), _sample_skill_gap(), SHORTLIST_THRESHOLD + 20, _sample_breakdown())
    assert result["would_shortlist"] is True


def test_score_below_threshold_does_not_shortlist():
    result = _build_mock_simulation(_sample_resume(), _sample_skill_gap(), SHORTLIST_THRESHOLD - 20, _sample_breakdown())
    assert result["would_shortlist"] is False


def test_confidence_increases_with_distance_from_threshold():
    near = _build_mock_simulation(_sample_resume(), _sample_skill_gap(), SHORTLIST_THRESHOLD + 1, _sample_breakdown())
    far = _build_mock_simulation(_sample_resume(), _sample_skill_gap(), SHORTLIST_THRESHOLD + 30, _sample_breakdown())
    confidence_rank = {"Low": 0, "Medium": 1, "High": 2}
    assert confidence_rank[far["shortlist_confidence"]] >= confidence_rank[near["shortlist_confidence"]]


def test_missing_phone_flagged_as_missing_element():
    result = _build_mock_simulation(_sample_resume(has_phone=False), _sample_skill_gap(), 80.0, _sample_breakdown())
    assert "Phone number" in result["missing_elements"]


def test_high_priority_missing_skills_become_concerns():
    result = _build_mock_simulation(_sample_resume(), _sample_skill_gap(missing_high=["Django"]), 50.0, _sample_breakdown())
    assert any("Django" in c for c in result["concerns"])


def test_output_always_has_required_keys():
    result = _build_mock_simulation(_sample_resume(), _sample_skill_gap(), 70.0, _sample_breakdown())
    required = {
        "would_shortlist", "shortlist_confidence", "standout_points",
        "concerns", "missing_elements", "competitiveness_assessment",
        "verdict_summary", "source",
    }
    assert required.issubset(result.keys())
    assert result["source"] == "mock_fallback"
