<!-- Badges: swap in your actual CI/license badge URLs once available -->
<!-- ![Build Status](https://img.shields.io/github/actions/workflow/status/<user>/<repo>/ci.yml) -->
<!-- ![License](https://img.shields.io/badge/license-MIT-blue.svg) -->

# AI Resume Analyzer & ATS Optimizer

A full-stack ATS Resume Analyzer platform that evaluates resumes against job descriptions using a deterministic rule-based scoring engine and Groq-powered AI insights.

The platform helps students, job seekers, and professionals understand how well their resumes align with specific job roles while providing recruiter-style feedback, interview preparation, resume improvements, and personalized career roadmaps.

<!-- **[Live Demo](#)** — add your deployed link here once hosted -->

---

## Table of Contents

- [Highlights](#highlights)
- [Why This Project?](#why-this-project)
- [Features](#features)
- [DevOps & Reliability](#devops--reliability)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Application Flow](#application-flow)
- [Implemented Pages](#implemented-pages)
- [API Endpoints](#api-endpoints)
- [Setup](#setup)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)

---

## Highlights

* Full-stack SaaS application (FastAPI + React/TypeScript)
* Rule-based, explainable ATS scoring engine
* Groq (Llama 3.3-70B) powered AI insights
* Clean architecture — Repository + Service layer
* Dockerized, with CI/CD and automated tests

---

## Why This Project?

Most ATS tools simply provide a score without explaining why.

This platform focuses on explainability.

Every ATS score is derived from transparent rules rather than machine learning black boxes. Users can clearly understand:

* Which skills matched
* Which skills are missing
* Why the score was assigned
* What improvements will increase recruiter visibility

AI is used only where language understanding genuinely adds value:

* Recruiter feedback
* Resume rewriting
* Interview preparation
* Career roadmaps

Core ATS scoring remains deterministic and fully explainable.

---

# Features

## Authentication

* User Registration
* User Login
* JWT Token Authentication
* Protected Routes
* Persistent Login Sessions

---

## Resume Parsing Engine

Upload resumes in:

* PDF
* DOCX

The system automatically extracts:

* Contact Information
* Education
* Skills
* Experience
* Projects
* Certifications

and converts them into structured JSON data.

---

## Job Description Analysis

Paste a job description and the system extracts:

* Required Skills
* Preferred Skills
* Technologies
* Responsibilities
* Qualifications
* Experience Requirements

---

## ATS Scoring Engine

Deterministic scoring across five weighted components:

| Component        | Weight |
| ---------------- | ------ |
| Skill Match      | 40%    |
| Keyword Coverage | 20%    |
| Experience Match | 20%    |
| Education Match  | 10%    |
| Completeness     | 10%    |

Every score includes an explanation so users understand how the result was calculated.

---

## Skill Gap Analysis

Shows:

### Matched Skills

Skills present in both:

* Resume
* Job Description

### Missing Skills

Skills expected by recruiters but not found in the resume.

Each missing skill includes:

* Priority Level
* Reason
* Improvement Suggestions

---

## AI Recruiter Review (Groq)

Simulates a recruiter performing a first-pass resume screening, weighted by both resume content and the ATS compatibility score.

Provides:

* Shortlist Decision
* Confidence Level
* Standout Points
* Concerns
* Missing Elements
* Competitiveness Assessment
* Final Verdict

---

## AI Resume Rewriter

Transforms weak resume bullets into stronger recruiter-friendly content.

Features:

* Strong Action Verbs
* ATS Keyword Optimization
* Improved Impact Statements
* No Fabricated Metrics

Example:

Before:

> Worked on a web application.

After:

> Built and deployed a full-stack web application using FastAPI and React, improving workflow efficiency and user experience.

---

## AI Interview Question Generator

Generates a realistic 10-question interview set based on:

* Resume
* Projects
* Skills
* Target Job Description

Question categories:

* Technical
* Behavioral
* Resume-Based
* Project-Based
* HR

Each question includes:

* Difficulty (Easy / Medium / Hard, with a realistic spread across the set)
* **Why This Matters** — what the question is actually assessing
* Expected Answer Points — usable as an interviewer's scoring rubric
* **Sample Strong Answer Outline** — the shape a strong answer should take, without a script to memorize
* **Red Flags** — concrete signs of a weak answer
* A natural follow-up question

Results appear inline and the page automatically scrolls to each tool's output as soon as it's generated.

---

## AI Career Roadmap Generator

Creates a personalized:

### 30 Day Plan

Foundation Building

### 60 Day Plan

Project Development

### 90 Day Plan

Interview Preparation & Job Search

Roadmaps are generated using actual skill gaps identified during ATS analysis.

---

## Dashboard

Interactive dashboard displaying:

* Total Resumes
* Job Descriptions
* Analysis History
* Latest ATS Score
* Recent Analyses (click any entry to open its full report)

---

# DevOps & Reliability

* **Containerization** — Full stack (frontend, backend, PostgreSQL, Redis) runs via Docker Compose for one-command local setup
* **Caching** — Redis caching on high-traffic endpoints to reduce database load and improve response times
* **CI/CD** — GitHub Actions pipeline runs linting, build verification, and the test suite on every push
* **Testing** — Unit and integration test suite covering 70–80% of backend code
* **Observability** — Structured logging and health-check endpoints for production monitoring
* **API Docs** — Interactive OpenAPI/Swagger docs auto-generated by FastAPI, available at `/docs`
* **Resilient AI calls** — structured-JSON enforcement, markdown-fence stripping, and retry-with-backoff on transient network errors when calling Groq, with a fully-featured deterministic mock fallback when no API key is configured

---

# Tech Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* JWT Authentication
* Pydantic
* Uvicorn
* Docker / Docker Compose
* GitHub Actions (CI/CD)
* Pytest

---

## Frontend

* React
* TypeScript
* Tailwind CSS
* React Router
* Axios
* Lucide Icons

---

## AI

* Groq API
* Llama Models

Example:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

# Architecture

```text
backend/
├── api/routes/
├── services/
├── repositories/
├── models/
├── schemas/
├── ai/
├── database/
├── utils/
└── core/

frontend/
├── pages/
├── components/
├── context/
└── lib/
```

---

## Architecture Patterns

### Repository Pattern

Database logic remains isolated from business logic.

### Service Layer

All business logic lives inside services.

### Dependency Injection

FastAPI dependencies manage:

* Authentication
* Database Sessions

### AI Layer Separation

The AI layer is completely isolated.

Responsibilities include:

* Prompt Construction
* Response Validation
* Structured JSON Parsing
* Fallback Responses

---

# Application Flow

```text
1. Upload Resume
        ↓
2. Resume Parsing
        ↓
3. Paste Job Description
        ↓
4. JD Analysis
        ↓
5. ATS Scoring Engine
        ↓
6. Skill Gap Analysis
        ↓
7. AI Recruiter Review
        ↓
8. Interview Questions
        ↓
9. Career Roadmap
```

---

# Implemented Pages

* Landing Page
* Login Page
* Register Page
* Dashboard
* Resume Analysis Page
* ATS Analysis Report
* Recruiter Feedback
* Interview Preparation
* Career Roadmap

---

# API Endpoints

## Authentication

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Resume

```http
POST /resume/upload
GET  /resume
GET  /resume/{id}
```

## Job Descriptions

```http
POST /job-description
GET  /job-description
GET  /job-description/{id}
```

## Analysis

```http
POST /analysis/run
GET  /analysis
GET  /analysis/{id}
```

## AI Features

```http
POST /ai/rewrite
POST /ai/recruiter
POST /ai/interview
POST /ai/roadmap
```

## Dashboard

```http
GET /dashboard
```

---

# Setup

## Prerequisites

* Python 3.11+
* Node.js 18+
* Docker & Docker Compose (for Option A)
* A [Groq API key](https://console.groq.com/keys) (optional — the app runs fully on deterministic mock responses without one)

---

## Option A — Docker Compose (recommended)

```bash
docker compose up --build
```

This starts the frontend, backend, PostgreSQL, and Redis together. The API will be available at `http://localhost:8000` (docs at `/docs`) and the frontend at `http://localhost:5173`.

---

## Option B — Manual Setup

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Environment Variables

```env
DATABASE_URL=postgresql://username:password@localhost/dbname

JWT_SECRET_KEY=your_secret_key

GROQ_API_KEY=your_api_key

GROQ_MODEL=llama-3.3-70b-versatile
```

> **Note:** Never commit a real `.env` file or API key. Copy `.env.example` to `.env` and fill in your own values locally.

---

# Screenshots

_Screenshots coming soon._

---

# Future Improvements

* Resume Version Comparison
* PDF Report Export
* Cover Letter Generator
* Job Recommendation Engine

---

