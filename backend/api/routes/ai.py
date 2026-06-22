"""
AI routes: resume rewriter, recruiter simulator, interview question
generator, career roadmap generator. All delegate to AIService.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from schemas.interview import InterviewQuestionRequest, InterviewQuestionResponse
from schemas.recruiter_simulation import RecruiterSimulationRequest, RecruiterSimulationResponse
from schemas.roadmap import RoadmapRequest, RoadmapResponse
from schemas.rewrite import RewriteRequest, RewriteResponse
from services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/rewrite", response_model=RewriteResponse)
def rewrite_content(
    payload: RewriteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Improves resume summary/bullet/project text. Optionally pass a
    job_description_id to align terminology with a specific target role.
    """
    service = AIService(db)
    return service.rewrite(current_user.id, payload)


@router.post("/recruiter", response_model=RecruiterSimulationResponse)
def recruiter_simulation(
    payload: RecruiterSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulates a recruiter's first-pass screening verdict for a resume
    against a specific job description.
    """
    service = AIService(db)
    return service.simulate_recruiter(current_user.id, payload)


@router.post("/interview", response_model=InterviewQuestionResponse)
def interview_questions(
    payload: InterviewQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a 10-question interview set (technical, behavioral,
    project-based, resume-based, HR) tailored to this resume + JD.
    """
    service = AIService(db)
    return service.generate_interview_questions(current_user.id, payload)


@router.post("/roadmap", response_model=RoadmapResponse)
def career_roadmap(
    payload: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generates a 30/60/90-day improvement plan targeting this
    candidate's actual missing skills for the target job description.
    """
    service = AIService(db)
    return service.generate_roadmap(current_user.id, payload)
