"""
JobDescription model. Stores raw pasted JD text and the extracted
structured requirements.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    parsed_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # parsed_data shape: { required_skills[], preferred_skills[], responsibilities[],
    #                       qualifications[], tools[], experience_required }

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        back_populates="job_description", cascade="all, delete-orphan"
    )
