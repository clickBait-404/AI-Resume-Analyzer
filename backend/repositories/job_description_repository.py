"""
Repository for JobDescription data access.
"""
from sqlalchemy.orm import Session

from models.job_description import JobDescription


class JobDescriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        title: str | None,
        company: str | None,
        raw_text: str,
        parsed_data: dict,
    ) -> JobDescription:
        jd = JobDescription(
            user_id=user_id,
            title=title,
            company=company,
            raw_text=raw_text,
            parsed_data=parsed_data,
        )
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        return jd

    def get_by_id(self, jd_id: int, user_id: int) -> JobDescription | None:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.id == jd_id, JobDescription.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[JobDescription]:
        return (
            self.db.query(JobDescription)
            .filter(JobDescription.user_id == user_id)
            .order_by(JobDescription.created_at.desc())
            .all()
        )
