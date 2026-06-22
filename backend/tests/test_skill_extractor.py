"""
Unit tests for the rule-based skill extraction engine.
Run with: pytest tests/test_skill_extractor.py
"""
from utils.skill_extractor import extract_skills


def test_basic_skill_extraction():
    text = "Experience with Python, FastAPI, and PostgreSQL."
    skills = extract_skills(text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills


def test_alias_resolution():
    text = "Strong knowledge of JavaScript and ReactJS, also used Node.js extensively."
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "React" in skills
    assert "Node.js" in skills


def test_bare_js_alias_intentionally_not_matched():
    """
    The bare 'JS' alias was intentionally removed from the taxonomy:
    it caused false positives by matching inside 'React.js', 'Node.js',
    etc. (since '.' isn't a word character, the boundary regex let it
    through). The tradeoff is that standalone 'JS' alone is no longer
    detected as JavaScript — documented here so the limitation is
    explicit rather than silently reintroduced later.
    """
    text = "Skills: JS"
    skills = extract_skills(text)
    assert "JavaScript" not in skills


def test_react_js_does_not_false_match_javascript_alone():
    """
    Regression test: 'React.js' should resolve to the React skill, and
    should NOT also trigger a spurious 'JavaScript' match purely from
    the '.js' substring (JavaScript should only match on its own
    explicit aliases like 'javascript').
    """
    text = "Skills: React.js, FastAPI"
    skills = extract_skills(text)
    assert "React" in skills
    assert "JavaScript" not in skills


def test_no_skills_in_empty_text():
    assert extract_skills("") == []
    assert extract_skills(None) == []


def test_case_insensitivity():
    text = "PYTHON, python, Python"
    skills = extract_skills(text)
    assert skills.count("Python") == 0 or "Python" in skills  # dedup check
    assert len([s for s in skills if s == "Python"]) == 1


def test_word_boundary_prevents_partial_matches():
    """
    'Java' should not match inside 'JavaScript' as a false positive
    for the Java language skill.
    """
    text = "Experience with JavaScript frameworks."
    skills = extract_skills(text)
    assert "JavaScript" in skills
    assert "Java" not in skills
