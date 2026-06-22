"""
Pydantic schemas for the AI resume rewriter endpoint.
"""
from pydantic import BaseModel, Field


class RewriteRequest(BaseModel):
    content_items: list[str] = Field(min_length=1, max_length=20)
    job_description_id: int | None = None  # optional, for keyword alignment context


class RewriteItem(BaseModel):
    original: str
    improved: str
    explanation: str


class RewriteResponse(BaseModel):
    rewrites: list[RewriteItem]
    source: str
