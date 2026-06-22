"""
AI Service: orchestrates the resume rewriter, recruiter simulator,
interview generator, and career advisor modules. Each method fetches
the needed resume/JD records, runs the relevant ai/* module, persists
the result where applicable, and returns it.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.career_advisor import generate_career_roadmap as ai_generate_career_roadmap
from ai.interview_generator import generate_interview_questions as ai_generate_interview_questions
from ai.recruiter_simulator import simulate_recruiter_review as ai_simulate_recruiter_review
from ai.resume_rewriter import rewrite_resume_content as ai_rewrite_resume_content
from repositories.career_roadmap_repository import CareerRoadmapRepository
from repositories.interview_question_repository import InterviewQuestionRepository
from repositories.job_description_repository import JobDescriptionRepository
from repositories.resume_repository import ResumeRepository
from schemas.interview import InterviewQuestionRequest
from schemas.recruiter_simulation import RecruiterSimulationRequest
from schemas.roadmap import RoadmapRequest
from schemas.rewrite import RewriteRequest
from services.ats_scoring_engine import run_ats_scoring


class AIService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_repo = ResumeRepository(db)
        self.jd_repo = JobDescriptionRepository(db)
        self.interview_repo = InterviewQuestionRepository(db)
        self.roadmap_repo = CareerRoadmapRepository(db)

    def _get_resume_and_jd(self, user_id: int, resume_id: int, jd_id: int):
        resume = self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
        jd = self.jd_repo.get_by_id(jd_id, user_id)
        if not jd:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
        return resume, jd

    def rewrite(self, user_id: int, payload: RewriteRequest) -> dict:
        jd_text = None
        if payload.job_description_id:
            jd = self.jd_repo.get_by_id(payload.job_description_id, user_id)
            if not jd:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
            jd_text = jd.raw_text

        return ai_rewrite_resume_content(payload.content_items, jd_text)

    def simulate_recruiter(self, user_id: int, payload: RecruiterSimulationRequest) -> dict:
        resume, jd = self._get_resume_and_jd(user_id, payload.resume_id, payload.job_description_id)

        scoring_result = run_ats_scoring(
            parsed_resume=resume.parsed_data,
            resume_raw_text=resume.raw_text,
            parsed_jd=jd.parsed_data,
            jd_raw_text=jd.raw_text,
        )

        return ai_simulate_recruiter_review(
            resume_raw_text=resume.raw_text,
            jd_raw_text=jd.raw_text,
            parsed_resume=resume.parsed_data,
            skill_gap=scoring_result["skill_gap"],
            overall_score=scoring_result["overall_score"],
            score_breakdown=scoring_result["score_breakdown"],
        )

    def generate_interview_questions(self, user_id: int, payload: InterviewQuestionRequest) -> dict:
        resume, jd = self._get_resume_and_jd(user_id, payload.resume_id, payload.job_description_id)

        result = ai_generate_interview_questions(
            resume_raw_text=resume.raw_text,
            jd_raw_text=jd.raw_text,
            parsed_resume=resume.parsed_data,
        )

        self.interview_repo.create(
            user_id=user_id,
            resume_id=resume.id,
            job_description_id=jd.id,
            questions=result["questions"],
            source=result["source"],
        )
        return result

    def generate_roadmap(self, user_id: int, payload: RoadmapRequest) -> dict:
        resume, jd = self._get_resume_and_jd(user_id, payload.resume_id, payload.job_description_id)

        scoring_result = run_ats_scoring(
            parsed_resume=resume.parsed_data,
            resume_raw_text=resume.raw_text,
            parsed_jd=jd.parsed_data,
            jd_raw_text=jd.raw_text,
        )
        # Prioritized missing skills, High priority first (already ordered that way
        # by compute_skill_gap: required/High items are added before preferred/Medium).
        missing_skills = [m["skill"] for m in scoring_result["skill_gap"]["missing_skills"]]

        result = ai_generate_career_roadmap(
            resume_raw_text=resume.raw_text,
            jd_raw_text=jd.raw_text,
            missing_skills=missing_skills,
            target_role=payload.target_role,
        )

        self.roadmap_repo.create(
            user_id=user_id,
            resume_id=resume.id,
            job_description_id=jd.id,
            target_role=payload.target_role,
            target_role_summary=result["target_role_summary"],
            plan_30_day=result["plan_30_day"],
            plan_60_day=result["plan_60_day"],
            plan_90_day=result["plan_90_day"],
            source=result["source"],
        )
        return result
