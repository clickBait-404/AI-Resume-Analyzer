"""
InterviewQuestionSet model. Stores a generated set of interview
questions tied to a resume + job description pair, so users can
revisit past generations from their dashboard.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class InterviewQuestionSet(Base):
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    job_description_id: Mapped[int] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True, nullable=False
    )

    questions: Mapped[list] = mapped_column(JSONB, nullable=False)
    # list[{category, question, difficulty, expected_answer_points, follow_up_question}]
    source: Mapped[str] = mapped_column(default="mock_fallback")  # "openai" | "mock_fallback"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
