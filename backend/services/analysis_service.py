"""
Analysis service: orchestrates the full ATS scoring engine plus
(optionally) the AI resume review, then persists the combined result.
This is the central workflow tying the resume and job description
together.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.resume_reviewer import generate_resume_review
from repositories.analysis_result_repository import AnalysisResultRepository
from repositories.job_description_repository import JobDescriptionRepository
from repositories.resume_repository import ResumeRepository
from schemas.analysis import AnalysisRunRequest
from services.ats_scoring_engine import run_ats_scoring


class AnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_repo = ResumeRepository(db)
        self.jd_repo = JobDescriptionRepository(db)
        self.result_repo = AnalysisResultRepository(db)

    def run(self, user_id: int, payload: AnalysisRunRequest):
        resume = self.resume_repo.get_by_id(payload.resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

        jd = self.jd_repo.get_by_id(payload.job_description_id, user_id)
        if not jd:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")

        scoring_result = run_ats_scoring(
            parsed_resume=resume.parsed_data,
            resume_raw_text=resume.raw_text,
            parsed_jd=jd.parsed_data,
            jd_raw_text=jd.raw_text,
        )

        ai_review = None
        if payload.include_ai_review:
            ai_review = generate_resume_review(
                resume_raw_text=resume.raw_text,
                jd_raw_text=jd.raw_text,
                parsed_resume=resume.parsed_data,
                skill_gap=scoring_result["skill_gap"],
                overall_score=scoring_result["overall_score"],
            )

        result = self.result_repo.create(
            user_id=user_id,
            resume_id=resume.id,
            job_description_id=jd.id,
            overall_score=scoring_result["overall_score"],
            score_breakdown=scoring_result["score_breakdown"],
            skill_gap=scoring_result["skill_gap"],
            ai_review=ai_review,
        )
        return result

    def get(self, result_id: int, user_id: int):
        result = self.result_repo.get_by_id(result_id, user_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis result not found.")
        return result

    def list_for_user(self, user_id: int):
        return self.result_repo.list_for_user(user_id)
