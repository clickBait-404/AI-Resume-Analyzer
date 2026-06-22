"""
Analysis routes: run the ATS scoring engine (+ optional AI review),
fetch a past result, list history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from schemas.analysis import AnalysisResultOut, AnalysisRunRequest
from services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/run", response_model=AnalysisResultOut, status_code=201)
def run_analysis(
    payload: AnalysisRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Runs the full ATS Scoring Engine against a (resume, job description)
    pair, and optionally generates an AI recruiter review.
    """
    service = AnalysisService(db)
    return service.run(current_user.id, payload)


@router.get("/{analysis_id}", response_model=AnalysisResultOut)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalysisService(db)
    return service.get(analysis_id, current_user.id)


@router.get("", response_model=list[AnalysisResultOut])
def list_analyses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalysisService(db)
    return service.list_for_user(current_user.id)
