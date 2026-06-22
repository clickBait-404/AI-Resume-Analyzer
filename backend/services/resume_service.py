"""
Resume service: orchestrates file validation, text extraction, and
rule-based structuring, then persists via the repository.
"""
import os
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.config import settings
from repositories.resume_repository import ResumeRepository
from services.resume_structurer import structure_resume
from services.resume_text_extractor import extract_text

ALLOWED_EXTENSIONS = {"pdf", "docx"}


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.resume_repo = ResumeRepository(db)

    async def upload_and_parse(self, user_id: int, file: UploadFile):
        file_ext = (file.filename or "").rsplit(".", 1)[-1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '.{file_ext}'. Only PDF and DOCX are supported.",
            )

        file_bytes = await file.read()
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
            )

        try:
            raw_text = extract_text(file_bytes, file_ext)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Could not extract text from file: {e}",
            )

        if not raw_text or len(raw_text.strip()) < 30:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract meaningful text from this file. It may be a scanned image without a text layer.",
            )

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, stored_filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        parsed_data = structure_resume(raw_text)

        resume = self.resume_repo.create(
            user_id=user_id,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_ext,
            raw_text=raw_text,
            parsed_data=parsed_data,
        )
        return resume

    def get(self, resume_id: int, user_id: int):
        resume = self.resume_repo.get_by_id(resume_id, user_id)
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
        return resume

    def list_for_user(self, user_id: int):
        return self.resume_repo.list_for_user(user_id)
