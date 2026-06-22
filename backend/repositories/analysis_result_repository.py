"""
Repository for AnalysisResult data access.
"""
from sqlalchemy.orm import Session

from models.analysis_result import AnalysisResult


class AnalysisResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        resume_id: int,
        job_description_id: int,
        overall_score: float,
        score_breakdown: dict,
        skill_gap: dict,
        ai_review: dict | None,
    ) -> AnalysisResult:
        result = AnalysisResult(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            overall_score=overall_score,
            score_breakdown=score_breakdown,
            skill_gap=skill_gap,
            ai_review=ai_review,
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_by_id(self, result_id: int, user_id: int) -> AnalysisResult | None:
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.id == result_id, AnalysisResult.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[AnalysisResult]:
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.user_id == user_id)
            .order_by(AnalysisResult.created_at.desc())
            .all()
        )
