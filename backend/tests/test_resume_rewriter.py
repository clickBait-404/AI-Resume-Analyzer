"""
Unit tests for the rule-based resume rewriter mock fallback.
Run with: pytest tests/test_resume_rewriter.py

Note: these test the mock fallback path directly (_build_mock_rewrite_single,
rewrite_resume_content with no API key set) since that's the
deterministic, testable part. The OpenAI path is exercised through
response_validator tests instead, since it depends on a live API call.
"""
from ai.resume_rewriter import _build_mock_rewrite_single, rewrite_resume_content


def test_spec_example_created_a_web_application():
    """
    Regression test for the exact example from the original spec:
    'Created a web application.' should become something with a
    stronger verb than 'Created'.
    """
    result = _build_mock_rewrite_single("Created a web application.")
    assert result["original"] == "Created a web application."
    assert result["improved"] != result["original"]
    assert "Developed" in result["improved"] or "Built" in result["improved"]


def test_weak_verb_substitution_produces_grammatical_output():
    """
    Regression test: 'Worked on X to build Y' must not produce a
    double-verb broken sentence like 'Built X to build Y'.
    """
    result = _build_mock_rewrite_single("Worked on the backend team to build APIs.")
    # Since this is a known-tricky case, the mock fallback should leave
    # it unchanged rather than producing broken grammar.
    assert "Built the backend team to build" not in result["improved"]


def test_gerund_after_verb_is_resolved():
    """
    'Responsible for managing the database' should not become
    'Owned managing the database' (verb + gerund reads as two stacked
    actions) — the gerund should be dropped so it reads as one action.
    """
    result = _build_mock_rewrite_single("Responsible for managing the database.")
    assert "Owned managing" not in result["improved"]
    assert result["improved"].startswith("Owned")


def test_already_strong_bullet_is_left_mostly_intact():
    strong = "Built a scalable microservices architecture using Docker and Kubernetes, reducing deployment time by 40%."
    result = _build_mock_rewrite_single(strong)
    assert result["improved"] == strong  # no weak verb, has a metric -> no changes needed


def test_never_fabricates_a_concrete_number():
    """
    The rewriter must never silently insert a fake specific number;
    if it suggests adding a metric, it must use a bracketed placeholder,
    not a fabricated figure.
    """
    result = _build_mock_rewrite_single("Created a web application.")
    # If a metric placeholder was added, it should be bracketed, not a bare digit sequence
    import re
    bare_numbers = re.findall(r"(?<!\[)\b\d+%(?!\])", result["improved"])
    assert bare_numbers == [], f"Found unbracketed fabricated number(s): {bare_numbers}"


def test_rewrite_resume_content_returns_one_result_per_input():
    items = ["Created a web application.", "Worked on testing.", "Responsible for the database."]
    result = rewrite_resume_content(items)
    assert len(result["rewrites"]) == len(items)
    assert result["source"] == "mock_fallback"


def test_empty_input_returns_empty_rewrites():
    result = rewrite_resume_content([])
    assert result["rewrites"] == []
    assert result["source"] == "none"
