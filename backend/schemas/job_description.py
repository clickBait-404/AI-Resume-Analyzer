"""
Pydantic schemas for job description analysis.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class JobDescriptionCreate(BaseModel):
    title: str | None = None
    company: str | None = None
    raw_text: str = Field(min_length=20)


class ParsedJobDescriptionData(BaseModel):
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    responsibilities: list[str] = []
    qualifications: list[str] = []
    tools: list[str] = []
    experience_required_years: int | None = None


class JobDescriptionOut(BaseModel):
    id: int
    title: str | None
    company: str | None
    parsed_data: ParsedJobDescriptionData
    created_at: datetime

    model_config = {"from_attributes": True}
