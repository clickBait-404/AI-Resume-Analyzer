"""
Pydantic schemas for the career roadmap generator endpoint.
"""
from pydantic import BaseModel


class RoadmapRequest(BaseModel):
    resume_id: int
    job_description_id: int
    target_role: str | None = None


class RoadmapPhase(BaseModel):
    focus: str
    weekly_goals: list[str]


class RoadmapResponse(BaseModel):
    target_role_summary: str
    plan_30_day: RoadmapPhase
    plan_60_day: RoadmapPhase
    plan_90_day: RoadmapPhase
    source: str
