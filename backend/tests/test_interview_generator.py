"""
Unit tests for the interview question generator mock fallback.
Run with: pytest tests/test_interview_generator.py
"""
from collections import Counter

from ai.interview_generator import _build_mock_questions


def test_always_generates_exactly_ten_questions():
    parsed_resume = {"skills": ["Python", "FastAPI"], "projects": [], "experience": []}
    result = _build_mock_questions(parsed_resume)
    assert len(result["questions"]) == 10


def test_two_questions_per_category():
    parsed_resume = {"skills": ["Python", "React"], "projects": [{"name": "X"}], "experience": [{"company": "Y", "title": "Eng"}]}
    result = _build_mock_questions(parsed_resume)
    counts = Counter(q["category"] for q in result["questions"])
    assert counts == {"Technical": 2, "Project-Based": 2, "Resume-Based": 2, "Behavioral": 2, "HR": 2}


def test_project_questions_reference_actual_project_name():
    parsed_resume = {"skills": [], "projects": [{"name": "AI Resume Analyzer"}], "experience": []}
    result = _build_mock_questions(parsed_resume)
    project_questions = [q for q in result["questions"] if q["category"] == "Project-Based"]
    assert any("AI Resume Analyzer" in q["question"] for q in project_questions)


def test_resume_based_questions_reference_actual_company():
    parsed_resume = {"skills": [], "projects": [], "experience": [{"company": "Acme Corp", "title": "Engineer"}]}
    result = _build_mock_questions(parsed_resume)
    resume_questions = [q for q in result["questions"] if q["category"] == "Resume-Based"]
    assert any("Acme Corp" in q["question"] for q in resume_questions)


def test_handles_completely_empty_resume_without_crashing():
    parsed_resume = {"skills": [], "projects": [], "experience": []}
    result = _build_mock_questions(parsed_resume)
    assert len(result["questions"]) == 10


def test_every_question_has_required_fields():
    parsed_resume = {"skills": ["Python"], "projects": [], "experience": []}
    result = _build_mock_questions(parsed_resume)
    required = {"category", "question", "difficulty", "expected_answer_points", "follow_up_question"}
    for q in result["questions"]:
        assert required.issubset(q.keys())
        assert q["difficulty"] in {"Easy", "Medium", "Hard"}
