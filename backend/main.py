"""
FastAPI application entrypoint.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models  # noqa: F401 - ensures all models are registered on Base.metadata
from api.routes import ai, analysis, auth, dashboard, job_description, resume
from core.config import settings
from database.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup for local/dev convenience.
    # In production, use Alembic migrations instead (see database/migrations/).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Rule-based ATS analysis, AI resume review, and interview coaching platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(job_description.router)
app.include_router(analysis.router)
app.include_router(ai.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
