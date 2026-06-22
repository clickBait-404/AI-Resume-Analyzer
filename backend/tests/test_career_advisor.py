"""
Unit tests for the career roadmap generator mock fallback.
Run with: pytest tests/test_career_advisor.py
"""
from ai.career_advisor import _build_mock_roadmap


def test_has_all_three_phases():
    result = _build_mock_roadmap(["Django", "GCP"], "Backend Engineer")
    assert "plan_30_day" in result
    assert "plan_60_day" in result
    assert "plan_90_day" in result


def test_each_phase_has_four_weekly_goals():
    result = _build_mock_roadmap(["Django"], "Backend Engineer")
    assert len(result["plan_30_day"]["weekly_goals"]) == 4
    assert len(result["plan_60_day"]["weekly_goals"]) == 4
    assert len(result["plan_90_day"]["weekly_goals"]) == 4


def test_30_day_plan_references_actual_missing_skill():
    result = _build_mock_roadmap(["Kubernetes"], "DevOps Engineer")
    assert "Kubernetes" in result["plan_30_day"]["focus"]
    assert any("Kubernetes" in g for g in result["plan_30_day"]["weekly_goals"])


def test_handles_no_target_role_gracefully():
    """
    Regression test: when target_role is None, the summary must not
    contain a double-article grammar error like 'A the target role'.
    """
    result = _build_mock_roadmap(["Django"], None)
    assert "A the" not in result["target_role_summary"]
    assert "a the" not in result["target_role_summary"].lower()


def test_handles_no_missing_skills_gracefully():
    result = _build_mock_roadmap([], "Backend Engineer")
    assert len(result["plan_30_day"]["weekly_goals"]) == 4
    assert "Backend Engineer" in result["target_role_summary"]


def test_handles_no_missing_skills_and_no_role():
    """Both edge cases at once — must not crash or produce broken grammar."""
    result = _build_mock_roadmap([], None)
    assert "A the" not in result["target_role_summary"]
    assert len(result["plan_30_day"]["weekly_goals"]) == 4


def test_source_is_mock_fallback():
    result = _build_mock_roadmap(["Django"], "Backend Engineer")
    assert result["source"] == "mock_fallback"
