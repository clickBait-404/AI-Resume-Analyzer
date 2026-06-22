"""
Dashboard routes: aggregated view of the user's history across
resumes, job descriptions, analyses, interview question sets, and
career roadmaps.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from repositories.analysis_result_repository import AnalysisResultRepository
from repositories.career_roadmap_repository import CareerRoadmapRepository
from repositories.interview_question_repository import InterviewQuestionRepository
from repositories.job_description_repository import JobDescriptionRepository
from repositories.resume_repository import ResumeRepository

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resumes = ResumeRepository(db).list_for_user(current_user.id)
    job_descriptions = JobDescriptionRepository(db).list_for_user(current_user.id)
    analyses = AnalysisResultRepository(db).list_for_user(current_user.id)
    interview_sets = InterviewQuestionRepository(db).list_for_user(current_user.id)
    roadmaps = CareerRoadmapRepository(db).list_for_user(current_user.id)

    score_trend = [
        {"date": a.created_at.isoformat(), "score": a.overall_score}
        for a in sorted(analyses, key=lambda x: x.created_at)
    ]

    # Skill coverage: how many distinct skills have appeared as "matched"
    # across all of this user's analyses, vs how many have ever been
    # "missing" — a real (not fake) aggregate metric derived from stored data.
    matched_skill_set: set[str] = set()
    missing_skill_set: set[str] = set()
    for a in analyses:
        matched_skill_set.update(a.skill_gap.get("matched_skills", []))
        missing_skill_set.update(m["skill"] for m in a.skill_gap.get("missing_skills", []))

    return {
        "resume_count": len(resumes),
        "job_description_count": len(job_descriptions),
        "analysis_count": len(analyses),
        "interview_question_set_count": len(interview_sets),
        "career_roadmap_count": len(roadmaps),
        "latest_score": analyses[0].overall_score if analyses else None,
        "score_trend": score_trend,
        "skill_coverage": {
            "distinct_matched_skills": sorted(matched_skill_set),
            "distinct_missing_skills": sorted(missing_skill_set - matched_skill_set),
        },
        "recent_analyses": [
            {
                "id": a.id,
                "overall_score": a.overall_score,
                "created_at": a.created_at.isoformat(),
            }
            for a in analyses[:10]
        ],
        "recent_interview_sets": [
            {"id": s.id, "question_count": len(s.questions), "created_at": s.created_at.isoformat()}
            for s in interview_sets[:5]
        ],
        "recent_roadmaps": [
            {"id": r.id, "target_role": r.target_role, "created_at": r.created_at.isoformat()}
            for r in roadmaps[:5]
        ],
    }


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analyses = AnalysisResultRepository(db).list_for_user(current_user.id)
    return [
        {
            "id": a.id,
            "resume_id": a.resume_id,
            "job_description_id": a.job_description_id,
            "overall_score": a.overall_score,
            "created_at": a.created_at.isoformat(),
        }
        for a in analyses
    ]
