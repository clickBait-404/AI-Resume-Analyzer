"""
Repository for CareerRoadmap data access.
"""
from sqlalchemy.orm import Session

from models.career_roadmap import CareerRoadmap


class CareerRoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        resume_id: int,
        job_description_id: int,
        target_role: str | None,
        target_role_summary: str,
        plan_30_day: dict,
        plan_60_day: dict,
        plan_90_day: dict,
        source: str,
    ) -> CareerRoadmap:
        record = CareerRoadmap(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            target_role=target_role,
            target_role_summary=target_role_summary,
            plan_30_day=plan_30_day,
            plan_60_day=plan_60_day,
            plan_90_day=plan_90_day,
            source=source,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, roadmap_id: int, user_id: int) -> CareerRoadmap | None:
        return (
            self.db.query(CareerRoadmap)
            .filter(CareerRoadmap.id == roadmap_id, CareerRoadmap.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[CareerRoadmap]:
        return (
            self.db.query(CareerRoadmap)
            .filter(CareerRoadmap.user_id == user_id)
            .order_by(CareerRoadmap.created_at.desc())
            .all()
        )
