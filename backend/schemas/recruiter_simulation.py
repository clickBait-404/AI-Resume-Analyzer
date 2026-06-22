"""
Pydantic schemas for the recruiter simulator endpoint.
"""
from pydantic import BaseModel


class RecruiterSimulationRequest(BaseModel):
    resume_id: int
    job_description_id: int


class RecruiterSimulationResponse(BaseModel):
    would_shortlist: bool
    shortlist_confidence: str
    standout_points: list[str]
    concerns: list[str]
    missing_elements: list[str]
    competitiveness_assessment: str
    verdict_summary: str
    source: str
