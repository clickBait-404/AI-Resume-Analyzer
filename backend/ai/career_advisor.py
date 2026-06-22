"""
Career Advisor / Roadmap Generator.

Generates a 30/60/90-day improvement plan targeting the candidate's
actual missing skills (from the ATS skill gap analysis), not generic
career advice.

Uses OpenAI when configured. The mock fallback builds week-by-week
goals directly from the prioritized missing-skill list so the plan is
genuinely specific to this candidate's gap, even without a live model.
"""
from ai.llm_client import get_structured_completion, is_live
from ai.prompt_manager import CAREER_ADVISOR_SYSTEM_PROMPT, build_career_advisor_user_prompt
from ai.response_validator import validate_career_roadmap


def _build_mock_roadmap(missing_skills: list[str], target_role: str | None) -> dict:
    role_label = target_role if target_role else "this role"

    # Take up to 3 highest-priority missing skills to focus the plan on.
    # (Caller passes them already ordered by priority - High first.)
    focus_skills = missing_skills[:3] if missing_skills else []
    skill_a = focus_skills[0] if len(focus_skills) > 0 else "a core skill for this role"
    skill_b = focus_skills[1] if len(focus_skills) > 1 else None
    skill_c = focus_skills[2] if len(focus_skills) > 2 else None

    plan_30_day = {
        "focus": f"Foundational learning of the highest-priority missing skill(s) for {role_label}: {', '.join(focus_skills) if focus_skills else 'core role fundamentals'}.",
        "weekly_goals": [
            f"Week 1: Complete an official getting-started guide or intro course for {skill_a}; build one small standalone exercise.",
            f"Week 2: {'Continue ' + skill_a + ' fundamentals, focusing on the parts most referenced in real job postings' if not skill_b else 'Start fundamentals for ' + skill_b}.",
            f"Week 3: {'Build a small script or component combining ' + skill_a + ' with a skill you already have' if not skill_c else 'Begin fundamentals for ' + skill_c}.",
            "Week 4: Review everything learned so far; identify which concepts still feel shaky and revisit them before moving to applied practice.",
        ],
    }

    plan_60_day = {
        "focus": f"Applied practice — build one real project that meaningfully uses {', '.join(focus_skills) if focus_skills else 'your core stack'}.",
        "weekly_goals": [
            "Week 5: Scope a small portfolio project that requires using the skills from the last phase together, not in isolation.",
            "Week 6: Build the core functionality of the project; aim for something working end-to-end, even if rough.",
            "Week 7: Add the parts that demonstrate the missing skills specifically and visibly — this is what you'll point to in interviews.",
            "Week 8: Write a clear README and push to GitHub; this becomes resume-ready evidence, not just practice.",
        ],
    }

    plan_90_day = {
        "focus": "Portfolio polish, resume/interview alignment, and active job search execution.",
        "weekly_goals": [
            "Week 9: Update your resume to explicitly reflect the new project and skills using specific, quantified bullets.",
            "Week 10: Re-run this ATS analysis against your updated resume and target JD to confirm the skill gap has closed.",
            "Week 11: Practice the interview question set generated for this role, focusing on the project you just built.",
            "Week 12: Begin actively applying, using the updated resume; track applications and iterate based on response rate.",
        ],
    }

    return {
        "target_role_summary": f"A candidate targeting {role_label}, working to close the gap on: {', '.join(focus_skills) if focus_skills else 'role-specific fundamentals'}.",
        "plan_30_day": plan_30_day,
        "plan_60_day": plan_60_day,
        "plan_90_day": plan_90_day,
        "source": "mock_fallback",
    }


def generate_career_roadmap(
    resume_raw_text: str,
    jd_raw_text: str,
    missing_skills: list[str],
    target_role: str | None = None,
) -> dict:
    if is_live():
        user_prompt = build_career_advisor_user_prompt(resume_raw_text, jd_raw_text, missing_skills, target_role)
        result = get_structured_completion(CAREER_ADVISOR_SYSTEM_PROMPT, user_prompt)
        if result and validate_career_roadmap(result):
            result["source"] = "openai"
            return result

    return _build_mock_roadmap(missing_skills, target_role)
