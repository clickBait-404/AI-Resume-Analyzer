"""
Pydantic schemas for the ATS analysis result — score breakdown,
skill gap, and AI review.
"""
from datetime import datetime

from pydantic import BaseModel


class AnalysisRunRequest(BaseModel):
    resume_id: int
    job_description_id: int
    include_ai_review: bool = True


class SubScore(BaseModel):
    score: float  # 0-100
    weight: float  # contribution weight to overall score
    explanation: str


class SkillMatchDetail(SubScore):
    matched: list[str] = []
    missing: list[str] = []


class ScoreBreakdown(BaseModel):
    skill_match: SkillMatchDetail
    experience_match: SubScore
    education_match: SubScore
    completeness: SubScore
    keyword_coverage: SubScore


class MissingSkill(BaseModel):
    skill: str
    priority: str  # High | Medium | Low
    reason: str


class SkillGap(BaseModel):
    matched_skills: list[str]
    missing_skills: list[MissingSkill]
    recommended_skills: list[str]


class AIReview(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    missing_keywords: list[str]
    writing_quality_feedback: str
    ats_optimization_suggestions: list[str]
    source: str  # "openai" | "mock_fallback"


class AnalysisResultOut(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    overall_score: float
    score_breakdown: ScoreBreakdown
    skill_gap: SkillGap
    ai_review: AIReview | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
