"""
Pydantic schemas for resume parsing.
"""
from datetime import datetime

from pydantic import BaseModel


class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    location: str | None = None


class EducationEntry(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None


class ExperienceEntry(BaseModel):
    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = []


class ProjectEntry(BaseModel):
    name: str | None = None
    description: str | None = None
    technologies: list[str] = []


class ParsedResumeData(BaseModel):
    contact_info: ContactInfo
    education: list[EducationEntry] = []
    skills: list[str] = []
    experience: list[ExperienceEntry] = []
    projects: list[ProjectEntry] = []
    certifications: list[str] = []


class ResumeOut(BaseModel):
    id: int
    original_filename: str
    file_type: str
    parsed_data: ParsedResumeData
    created_at: datetime

    model_config = {"from_attributes": True}
