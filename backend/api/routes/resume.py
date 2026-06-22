"""
Resume routes: upload + parse, fetch, list.
"""
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database.session import get_db
from models.user import User
from schemas.resume import ResumeOut
from services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeOut, status_code=201)
async def upload_resume(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads a resume file (PDF or DOCX), extracts text, and runs the
    rule-based structuring engine in a single step.
    """
    service = ResumeService(db)
    resume = await service.upload_and_parse(current_user.id, file)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResumeService(db)
    return service.list_for_user(current_user.id)


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ResumeService(db)
    return service.get(resume_id, current_user.id)
