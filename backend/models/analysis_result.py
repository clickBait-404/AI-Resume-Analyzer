"""
AnalysisResult model. The output of running the ATS Scoring Engine
against a (resume, job_description) pair. Fully explainable —
every sub-score is stored, not just the final number.
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True, nullable=False
    )

    overall_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100

    score_breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # { skill_match: {score, matched[], missing[], explanation},
    #   experience_match: {...}, education_match: {...},
    #   completeness: {...}, keyword_coverage: {...} }

    skill_gap: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # { matched_skills[], missing_skills[ {skill, priority} ], recommended_skills[] }

    ai_review: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # { strengths[], weaknesses[], missing_keywords[], writing_feedback, ats_suggestions[] }

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="analysis_results")
    job_description: Mapped["JobDescription"] = relationship(back_populates="analysis_results")
