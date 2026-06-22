"""
Job description service: orchestrates rule-based structuring and
persistence.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from repositories.job_description_repository import JobDescriptionRepository
from schemas.job_description import JobDescriptionCreate
from services.jd_structurer import structure_job_description


class JobDescriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.jd_repo = JobDescriptionRepository(db)

    def create(self, user_id: int, payload: JobDescriptionCreate):
        parsed_data = structure_job_description(payload.raw_text)
        return self.jd_repo.create(
            user_id=user_id,
            title=payload.title,
            company=payload.company,
            raw_text=payload.raw_text,
            parsed_data=parsed_data,
        )

    def get(self, jd_id: int, user_id: int):
        jd = self.jd_repo.get_by_id(jd_id, user_id)
        if not jd:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found.")
        return jd

    def list_for_user(self, user_id: int):
        return self.jd_repo.list_for_user(user_id)
