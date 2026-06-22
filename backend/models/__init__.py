"""
Import all models here so SQLAlchemy's Base.metadata is aware of them
(needed for create_all / Alembic autogenerate to discover tables).
"""
from models.analysis_result import AnalysisResult  # noqa: F401
from models.career_roadmap import CareerRoadmap  # noqa: F401
from models.interview_question_set import InterviewQuestionSet  # noqa: F401
from models.job_description import JobDescription  # noqa: F401
from models.resume import Resume  # noqa: F401
from models.skill import Skill  # noqa: F401
from models.user import User  # noqa: F401
