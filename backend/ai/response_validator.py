"""
Validates AI responses against the expected schema before they're
trusted by the rest of the application. If the LLM returns malformed
JSON or missing fields, we catch it here rather than letting it leak
into the API response.
"""


def validate_resume_review(data: dict) -> bool:
    required_keys = {
        "strengths",
        "weaknesses",
        "missing_keywords",
        "writing_quality_feedback",
        "ats_optimization_suggestions",
    }
    if not isinstance(data, dict):
        return False
    if not required_keys.issubset(data.keys()):
        return False
    for list_key in ("strengths", "weaknesses", "missing_keywords", "ats_optimization_suggestions"):
        if not isinstance(data[list_key], list):
            return False
    if not isinstance(data["writing_quality_feedback"], str):
        return False
    return True


def validate_resume_rewrite(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    if "rewrites" not in data or not isinstance(data["rewrites"], list):
        return False
    if len(data["rewrites"]) == 0:
        return False
    for item in data["rewrites"]:
        if not isinstance(item, dict):
            return False
        if not all(k in item for k in ("original", "improved", "explanation")):
            return False
        if not all(isinstance(item[k], str) for k in ("original", "improved", "explanation")):
            return False
    return True


def validate_recruiter_simulation(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    required_keys = {
        "would_shortlist",
        "shortlist_confidence",
        "standout_points",
        "concerns",
        "missing_elements",
        "competitiveness_assessment",
        "verdict_summary",
    }
    if not required_keys.issubset(data.keys()):
        return False
    if not isinstance(data["would_shortlist"], bool):
        return False
    if data["shortlist_confidence"] not in ("High", "Medium", "Low"):
        return False
    for list_key in ("standout_points", "concerns", "missing_elements"):
        if not isinstance(data[list_key], list):
            return False
    for str_key in ("competitiveness_assessment", "verdict_summary"):
        if not isinstance(data[str_key], str):
            return False
    return True


VALID_INTERVIEW_CATEGORIES = {"Technical", "Behavioral", "Project-Based", "Resume-Based", "HR"}
VALID_DIFFICULTIES = {"Easy", "Medium", "Hard"}


def validate_interview_questions(data: dict) -> bool:
    """
    Upgraded schema: each question now also requires
    "why_this_matters" (str) and "red_flags" (list) alongside the
    original fields. "sample_strong_answer_outline" is validated as a
    string when present, but is treated as optional here so that
    older cached/mock responses generated before this upgrade don't
    hard-fail validation — the generator itself always includes it
    going forward.
    """
    if not isinstance(data, dict):
        return False
    if "questions" not in data or not isinstance(data["questions"], list):
        return False
    if len(data["questions"]) == 0:
        return False
    for q in data["questions"]:
        if not isinstance(q, dict):
            return False
        required = {
            "category",
            "question",
            "difficulty",
            "why_this_matters",
            "expected_answer_points",
            "red_flags",
            "follow_up_question",
        }
        if not required.issubset(q.keys()):
            return False
        if q["category"] not in VALID_INTERVIEW_CATEGORIES:
            return False
        if q["difficulty"] not in VALID_DIFFICULTIES:
            return False
        if not isinstance(q["question"], str) or not isinstance(q["follow_up_question"], str):
            return False
        if not isinstance(q["why_this_matters"], str):
            return False
        if not isinstance(q["expected_answer_points"], list):
            return False
        if not isinstance(q["red_flags"], list):
            return False
        if "sample_strong_answer_outline" in q and not isinstance(q["sample_strong_answer_outline"], str):
            return False
    return True


def _validate_roadmap_phase(phase: dict, expected_week_count: int = 4) -> bool:
    if not isinstance(phase, dict):
        return False
    if "focus" not in phase or not isinstance(phase["focus"], str):
        return False
    if "weekly_goals" not in phase or not isinstance(phase["weekly_goals"], list):
        return False
    if len(phase["weekly_goals"]) == 0:
        return False
    return all(isinstance(g, str) for g in phase["weekly_goals"])


def validate_career_roadmap(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    required_keys = {"target_role_summary", "plan_30_day", "plan_60_day", "plan_90_day"}
    if not required_keys.issubset(data.keys()):
        return False
    if not isinstance(data["target_role_summary"], str):
        return False
    for phase_key in ("plan_30_day", "plan_60_day", "plan_90_day"):
        if not _validate_roadmap_phase(data[phase_key]):
            return False
    return True