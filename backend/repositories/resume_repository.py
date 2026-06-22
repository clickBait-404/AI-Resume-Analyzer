"""
Repository for Resume data access.
"""
from sqlalchemy.orm import Session

from models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        original_filename: str,
        file_path: str,
        file_type: str,
        raw_text: str,
        parsed_data: dict,
    ) -> Resume:
        resume = Resume(
            user_id=user_id,
            original_filename=original_filename,
            file_path=file_path,
            file_type=file_type,
            raw_text=raw_text,
            parsed_data=parsed_data,
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_by_id(self, resume_id: int, user_id: int) -> Resume | None:
        return self.db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()

    def list_for_user(self, user_id: int) -> list[Resume]:
        return self.db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.created_at.desc()).all()
