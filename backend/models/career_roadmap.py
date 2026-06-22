"""
CareerRoadmap model. Stores a generated 30/60/90-day plan tied to a
resume + job description pair.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database.session import Base


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True, nullable=False
    )

    target_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_role_summary: Mapped[str] = mapped_column(nullable=False)
    plan_30_day: Mapped[dict] = mapped_column(JSONB, nullable=False)
    plan_60_day: Mapped[dict] = mapped_column(JSONB, nullable=False)
    plan_90_day: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source: Mapped[str] = mapped_column(default="mock_fallback")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
