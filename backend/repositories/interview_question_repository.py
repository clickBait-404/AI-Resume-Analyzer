"""
Repository for InterviewQuestionSet data access.
"""
from sqlalchemy.orm import Session

from models.interview_question_set import InterviewQuestionSet


class InterviewQuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        resume_id: int,
        job_description_id: int,
        questions: list,
        source: str,
    ) -> InterviewQuestionSet:
        record = InterviewQuestionSet(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            questions=questions,
            source=source,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, set_id: int, user_id: int) -> InterviewQuestionSet | None:
        return (
            self.db.query(InterviewQuestionSet)
            .filter(InterviewQuestionSet.id == set_id, InterviewQuestionSet.user_id == user_id)
            .first()
        )

    def list_for_user(self, user_id: int) -> list[InterviewQuestionSet]:
        return (
            self.db.query(InterviewQuestionSet)
            .filter(InterviewQuestionSet.user_id == user_id)
            .order_by(InterviewQuestionSet.created_at.desc())
            .all()
        )
