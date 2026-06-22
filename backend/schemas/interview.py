"""
Pydantic schemas for the interview question generator endpoint.
"""
from pydantic import BaseModel


class InterviewQuestionRequest(BaseModel):
    resume_id: int
    job_description_id: int


class InterviewQuestion(BaseModel):
    category: str
    question: str
    difficulty: str
    expected_answer_points: list[str]
    follow_up_question: str


class InterviewQuestionResponse(BaseModel):
    questions: list[InterviewQuestion]
    source: str
