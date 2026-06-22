"""
Job description routes: submit + parse, fetch, list.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from schemas.job_description import JobDescriptionCreate, JobDescriptionOut
from services.job_description_service import JobDescriptionService

router = APIRouter(prefix="/job-description", tags=["Job Description"])


@router.post("", response_model=JobDescriptionOut, status_code=201)
def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = JobDescriptionService(db)
    return service.create(current_user.id, payload)


@router.get("", response_model=list[JobDescriptionOut])
def list_job_descriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = JobDescriptionService(db)
    return service.list_for_user(current_user.id)


@router.get("/{jd_id}", response_model=JobDescriptionOut)
def get_job_description(
    jd_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = JobDescriptionService(db)
    return service.get(jd_id, current_user.id)
