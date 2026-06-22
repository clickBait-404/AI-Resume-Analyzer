"""
Unit tests for ai/response_validator.py — these guard the contract
that the OpenAI live path must satisfy, independent of any actual
API call.
Run with: pytest tests/test_response_validator.py
"""
from ai.response_validator import (
    validate_career_roadmap,
    validate_interview_questions,
    validate_recruiter_simulation,
    validate_resume_review,
    validate_resume_rewrite,
)


def test_resume_review_valid():
    data = {
        "strengths": ["a"], "weaknesses": ["b"], "missing_keywords": ["c"],
        "writing_quality_feedback": "text", "ats_optimization_suggestions": ["d"],
    }
    assert validate_resume_review(data) is True


def test_resume_review_missing_key_fails():
    assert validate_resume_review({"strengths": ["a"]}) is False


def test_resume_review_wrong_type_fails():
    data = {
        "strengths": "not a list", "weaknesses": ["b"], "missing_keywords": ["c"],
        "writing_quality_feedback": "text", "ats_optimization_suggestions": ["d"],
    }
    assert validate_resume_review(data) is False


def test_resume_rewrite_valid():
    assert validate_resume_rewrite({"rewrites": [{"original": "a", "improved": "b", "explanation": "c"}]}) is True


def test_resume_rewrite_empty_list_fails():
    assert validate_resume_rewrite({"rewrites": []}) is False


def test_resume_rewrite_missing_field_fails():
    assert validate_resume_rewrite({"rewrites": [{"original": "a", "improved": "b"}]}) is False


def test_recruiter_simulation_valid():
    data = {
        "would_shortlist": True, "shortlist_confidence": "High",
        "standout_points": [], "concerns": [], "missing_elements": [],
        "competitiveness_assessment": "x", "verdict_summary": "y",
    }
    assert validate_recruiter_simulation(data) is True


def test_recruiter_simulation_bad_confidence_value_fails():
    data = {
        "would_shortlist": True, "shortlist_confidence": "Definitely",
        "standout_points": [], "concerns": [], "missing_elements": [],
        "competitiveness_assessment": "x", "verdict_summary": "y",
    }
    assert validate_recruiter_simulation(data) is False


def test_recruiter_simulation_wrong_type_for_shortlist_fails():
    data = {
        "would_shortlist": "yes", "shortlist_confidence": "High",
        "standout_points": [], "concerns": [], "missing_elements": [],
        "competitiveness_assessment": "x", "verdict_summary": "y",
    }
    assert validate_recruiter_simulation(data) is False


def test_interview_questions_valid():
    data = {"questions": [{
        "category": "Technical", "question": "q", "difficulty": "Easy",
        "expected_answer_points": ["p"], "follow_up_question": "f",
    }]}
    assert validate_interview_questions(data) is True


def test_interview_questions_bad_category_fails():
    data = {"questions": [{
        "category": "Random", "question": "q", "difficulty": "Easy",
        "expected_answer_points": ["p"], "follow_up_question": "f",
    }]}
    assert validate_interview_questions(data) is False


def test_interview_questions_bad_difficulty_fails():
    data = {"questions": [{
        "category": "Technical", "question": "q", "difficulty": "Impossible",
        "expected_answer_points": ["p"], "follow_up_question": "f",
    }]}
    assert validate_interview_questions(data) is False


def test_career_roadmap_valid():
    phase = {"focus": "f", "weekly_goals": ["w1", "w2"]}
    data = {"target_role_summary": "s", "plan_30_day": phase, "plan_60_day": phase, "plan_90_day": phase}
    assert validate_career_roadmap(data) is True


def test_career_roadmap_missing_phase_fails():
    phase = {"focus": "f", "weekly_goals": ["w1"]}
    data = {"target_role_summary": "s", "plan_30_day": phase, "plan_60_day": phase}
    assert validate_career_roadmap(data) is False


def test_career_roadmap_empty_weekly_goals_fails():
    phase = {"focus": "f", "weekly_goals": []}
    data = {"target_role_summary": "s", "plan_30_day": phase, "plan_60_day": phase, "plan_90_day": phase}
    assert validate_career_roadmap(data) is False
