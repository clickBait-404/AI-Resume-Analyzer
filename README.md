# AI Resume Analyzer & ATS Optimizer

A rule-based (no ML) resume/job-description matching engine with an OpenAI-powered
recruiter review layer, plus a React frontend. Built as a portfolio-grade full-stack
app demonstrating clean architecture, deterministic scoring logic, and pragmatic AI
integration.

> **Status:** Backend is complete (5 AI modules, full ATS engine, auth, persistence).
> Frontend covers the critical path end-to-end: landing page → register/login →
> upload resume + paste JD → run analysis → view explainable score breakdown. Other
> pages (recruiter simulator, interview prep, roadmap, full history) are designed-for
> in the API client but not yet built as pages — see [Roadmap](#roadmap).

## Why rule-based, not ML?

This system deliberately avoids scikit-learn, TF-IDF, cosine similarity, and any
trained model for scoring. Every score is traceable to a specific rule (e.g. "5 of 7
required skills matched") rather than an opaque similarity number. This is also more
honest about what it's doing — real ATS systems are mostly keyword/rule engines, not
ML models, so this mirrors reality rather than dressing up a class project as something
it isn't.

OpenAI is used *only* for the qualitative recruiter-style review (strengths,
weaknesses, writing feedback) — the part that genuinely benefits from language
understanding rather than pattern matching.

## Features (implemented in this slice)

- **JWT Authentication** — register/login, protected routes
- **Resume Parsing Engine** — PDF/DOCX upload → structured JSON (contact info,
  education, skills, experience, projects, certifications) via rule-based extraction
- **Job Description Analyzer** — paste a JD → structured required/preferred skills,
  responsibilities, qualifications, tools, years of experience
- **ATS Scoring Engine** — deterministic 0–100 score across 5 weighted, fully
  explainable components: Skill Match (40%), Keyword Coverage (20%), Experience
  Match (20%), Education Match (10%), Completeness (10%)
- **Skill Gap Analysis** — matched/missing/recommended skills with High/Medium/Low
  priority, each with a stated reason
- **AI Resume Review** — strengths/weaknesses/missing keywords/writing
  feedback/ATS suggestions
- **AI Resume Rewriter** — transforms weak bullets into stronger ones; mock fallback
  uses deterministic weak-verb substitution and never fabricates metrics (uses
  bracketed placeholders like `[X%]` instead)
- **Recruiter Simulator** — shortlist verdict, standout points, concerns, missing
  elements, competitiveness assessment; mock fallback's verdict is derived from the
  real ATS score so it stays internally consistent with the rest of the analysis
- **Interview Question Generator** — 10 questions (2 each: Technical, Behavioral,
  Project-Based, Resume-Based, HR) with expected-answer rubric points and follow-ups;
  mock fallback's Project-Based and Resume-Based questions reference the candidate's
  actual project names and company names
- **Career Roadmap Generator** — 30/60/90-day plan with weekly goals; mock fallback
  prioritizes the candidate's actual highest-priority missing skills, not generic advice
- **Dashboard & History** — score trend, skill coverage (aggregated from real stored
  analyses), recent analyses/interview sets/roadmaps, aggregate counts

All five AI modules follow the same pattern: build prompt → call OpenAI → validate
response against a strict schema → fall back to a data-driven mock if no API key is
set or the live call fails/returns malformed JSON. Every mock fallback is genuinely
derived from the candidate's real parsed data — none of them return static
placeholder text.

## Not yet built (see Roadmap)

The React frontend is designed-for in the schema/architecture (CORS is configured,
every endpoint returns clean JSON) but not yet implemented.

## Architecture

```
backend/
├── api/routes/        # FastAPI route handlers (thin — delegate to services)
├── services/           # Business logic & orchestration
├── repositories/        # Data access layer (SQLAlchemy queries only)
├── models/              # SQLAlchemy ORM models
├── schemas/              # Pydantic request/response contracts
├── ai/                    # OpenAI integration: client, prompts, validators, modules
├── database/               # Engine/session setup
├── utils/                    # Skill taxonomy + extraction engine (pure functions)
├── core/                      # Config, security (JWT/hashing), shared dependencies
└── tests/                      # Unit tests
```

**Patterns used:**
- **Repository Pattern** — routes never touch SQLAlchemy directly
- **Service Layer** — all business logic lives in `services/`, routes are thin
- **Dependency Injection** — FastAPI's `Depends()` for DB sessions and current user
- **Separation of AI concerns** — `llm_client.py` is the *only* file that imports the
  `openai` package; every AI module builds a prompt, calls the client, validates the
  response, and falls back to a mock if needed

### Data flow for a full analysis

```
1. POST /resume/upload      → extract_text() → structure_resume() → stored as Resume
2. POST /job-description     → structure_job_description() → stored as JobDescription
3. POST /analysis/run         → run_ats_scoring(resume, jd)
                                     ↓
                              score_breakdown + skill_gap (deterministic)
                                     ↓
                              generate_resume_review() (OpenAI or mock)
                                     ↓
                              stored as AnalysisResult, returned to client

4. POST /ai/rewrite           → rewrite_resume_content() — improve bullets/summary
5. POST /ai/recruiter         → run_ats_scoring() + simulate_recruiter_review()
6. POST /ai/interview         → generate_interview_questions() → stored as InterviewQuestionSet
7. POST /ai/roadmap           → run_ats_scoring() (for missing skills) + generate_career_roadmap()
                                     → stored as CareerRoadmap
```

## Frontend

Built with React 18, TypeScript, Tailwind CSS, React Router, and Framer Motion (per
spec). Recharts is installed but not yet wired into a chart — the dashboard currently
shows real numbers in stat cards rather than a fabricated chart, since a chart with
only 1-2 data points looks worse than no chart (see Known Limitations).

**Design direction:** warm paper background, a serif display face (Fraunces) paired
with Inter for body text and JetBrains Mono for scores/skill tags — deliberately
avoiding the neon-gradient/glassmorphism look the spec explicitly ruled out. The
landing page's signature visual is a resume document with a scan line sweeping down
it, highlighting skill terms as it passes — a literal depiction of "this is what the
algorithm sees," which is the actual product thesis, rather than a generic dashboard
mockup.

```
frontend/src/
├── pages/              # One file per route
├── components/          # Reusable UI primitives (Button, Card, TextField, Navbar...)
├── context/               # AuthContext — app-wide auth state
└── lib/
    ├── api.ts              # Typed axios client, one method per backend endpoint
    └── types.ts              # TypeScript types mirroring backend Pydantic schemas exactly
```

**Pages implemented:** Landing, Login, Register, Dashboard, Analyze (upload + JD
paste), Analysis Result (full explainable score breakdown + skill gap + AI review).

**Auth flow:** JWT stored in `localStorage`; on app load, the token is validated
against a real `GET /auth/me` call (added to the backend specifically to support
this) rather than trusted blindly — an expired or tampered token is caught
immediately instead of surfacing as a confusing 401 later on a protected page.

## Database Schema

5 core tables plus the two AI-output tables added in this pass:

| Table | Purpose |
|---|---|
| `users` | Auth + profile |
| `resumes` | Original file ref + extracted raw text + structured JSON |
| `job_descriptions` | Raw JD text + structured requirements |
| `analysis_results` | Score breakdown, skill gap, AI review — fully explainable, nothing is black-boxed |
| `skills` | Canonical skill taxonomy (for future DB-driven matching; currently the taxonomy lives in `utils/skill_taxonomy.py` as code for simplicity) |
| `interview_questions` | Generated question sets, tied to a resume + JD pair |
| `career_roadmaps` | Generated 30/60/90-day plans, tied to a resume + JD pair |

`user_settings` from the original spec is deferred — no user-configurable settings
exist yet to justify the table.

All foreign keys cascade on delete. Indexes on all foreign keys and lookup fields
(`email`, `canonical_name`).

## Setup

### Option A — Docker Compose (recommended, matches the spec exactly)

```bash
cd ats-platform
cp backend/.env.example backend/.env
# Optionally add your OPENAI_API_KEY to backend/.env — leave blank to use mock AI responses
docker compose up --build
```

The API will be live at `http://localhost:8000` (interactive docs at `/docs`), and
the frontend at `http://localhost:5173`.

### Option B — Local Python (no Docker)

Requires a local PostgreSQL instance.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set DATABASE_URL to your local Postgres connection string
uvicorn main:app --reload
```

### Running tests

```bash
cd backend
pytest -v
```

### Frontend-only local dev (no Docker)

Requires the backend running separately (either Docker or `uvicorn main:app --reload`).

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`. The Vite dev server proxies `/api/*` to
`http://localhost:8000` by default (see `vite.config.ts` — this target is overridden
via `VITE_API_PROXY_TARGET` when running in Docker Compose, where the backend is
reachable at the service name `backend`, not `localhost`).

```bash
cd frontend
npm run test       # vitest
```

## API Documentation

Full interactive docs are auto-generated at `/docs` (Swagger) and `/redoc`. Summary:

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create account, returns JWT |
| POST | `/auth/login` | Authenticate, returns JWT |
| POST | `/resume/upload` | Upload PDF/DOCX, returns parsed structured data |
| GET | `/resume` | List your uploaded resumes |
| GET | `/resume/{id}` | Get one resume's parsed data |
| POST | `/job-description` | Submit JD text, returns parsed structured data |
| GET | `/job-description` | List your submitted JDs |
| GET | `/job-description/{id}` | Get one JD's parsed data |
| POST | `/analysis/run` | Run ATS scoring (+ optional AI review) on a resume/JD pair |
| GET | `/analysis/{id}` | Get one analysis result |
| GET | `/analysis` | List your analysis history |
| POST | `/ai/rewrite` | Improve resume summary/bullet/project text |
| POST | `/ai/recruiter` | Simulate a recruiter's first-pass shortlist decision |
| POST | `/ai/interview` | Generate a 10-question interview set for a resume/JD pair |
| POST | `/ai/roadmap` | Generate a 30/60/90-day improvement plan |
| GET | `/dashboard` | Aggregated stats, score trend, skill coverage |
| GET | `/history` | Flat list of past analyses |

All routes except `/auth/*` and `/health` require `Authorization: Bearer <token>`.

### Example: full flow with curl

```bash
# 1. Register
TOKEN=$(curl -s -X POST localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Upload resume
RESUME_ID=$(curl -s -X POST localhost:8000/resume/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/resume.pdf" | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

# 3. Submit job description
JD_ID=$(curl -s -X POST localhost:8000/job-description \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"raw_text":"We need a backend engineer with Python, FastAPI, PostgreSQL..."}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")

# 4. Run analysis
curl -s -X POST localhost:8000/analysis/run \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"resume_id\":$RESUME_ID,\"job_description_id\":$JD_ID,\"include_ai_review\":true}"

# 5. Generate interview questions for the same pair
curl -s -X POST localhost:8000/ai/interview \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"resume_id\":$RESUME_ID,\"job_description_id\":$JD_ID}"

# 6. Generate a 30/60/90-day roadmap
curl -s -X POST localhost:8000/ai/roadmap \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d "{\"resume_id\":$RESUME_ID,\"job_description_id\":$JD_ID,\"target_role\":\"Backend Engineer\"}"
```

## What was actually verified vs. written

In the interest of not overstating confidence:

**Backend** — the pure-Python business logic (skill extraction, resume/JD structuring,
ATS scoring, all 5 AI modules' mock-fallback paths) was executed directly against
realistic sample data during development, and 54 unit tests covering that logic all
pass. Several real bugs were caught and fixed this way — e.g. a broken international
phone-number regex, a false-positive skill match ("React.js" incorrectly also tagging
"JavaScript"), and grammar bugs in the rule-based rewriter and roadmap generator.
The FastAPI route layer, SQLAlchemy models, and JWT auth flow are written against
well-documented, stable APIs but were **not** executed end-to-end against a running
server or live Postgres instance — the development environment had no network access
to install the framework dependencies.

**Frontend** — the development environment also had no network access to run
`npm install`, `tsc`, or `vitest`, so no React component was ever actually rendered or
compiled during development. To compensate, every cross-file import was statically
verified (a script confirmed all 17 TS/TSX files' imports resolve to real exports in
their target files), every API call's URL path was checked character-for-character
against the actual backend route definitions, and brace/paren/bracket balance was
checked across all files. Two real bugs were still caught this way: a `helperText`
prop used in `RegisterPage` before it existed on `TextField` (fixed), and a Vite proxy
target hardcoded to `localhost` that would have silently failed inside Docker Compose
where the backend lives at a different hostname (fixed). Given the lack of a compiler
in the loop, treat the frontend's first real `npm install && npm run dev` as the actual
smoke test, more so than for the backend.

## Known limitations (stated honestly, not hidden)

- **"X or Y" requirements in a JD** (e.g. "FastAPI or Django") are currently scored as
  two independent required skills rather than an either/or — a resume with only one of
  them will show the other as "missing" even though the requirement is satisfied. Fixing
  this needs a small grammar layer over the qualifications text; flagged for a follow-up.
- **Experience-years estimation** is a coarse proxy (role count × 1.5 years) since
  reliably parsing date ranges across all resume formats is its own significant project.
  This is stated in the score's `explanation` field rather than presented as precise.
- **Section detection** relies on common heading text (e.g. "Experience", "Education").
  Resumes with unconventional or creative section titles may parse incompletely.
- Skill taxonomy currently lives in code (`utils/skill_taxonomy.py`) rather than being
  fully DB-driven through the `skills` table — the table exists and is ready, but admin
  CRUD on it wasn't built in this pass.
- The dashboard's score trend chart isn't built yet — `recharts` is installed and the
  backend already returns real `score_trend` data, but with most users having only 1-2
  analyses early on, a line chart would be more misleading than informative until
  there's a realistic amount of history. The raw data is shown as a number list instead.
- The frontend's `/auth/me` round-trip on every page load adds a network request before
  a protected page can render. For a production app this would be worth caching more
  aggressively (e.g. a short-lived in-memory cache), but correctness was prioritized
  over that optimization here.

## Roadmap

- [ ] Remaining frontend pages: recruiter simulator, interview question generator,
      career roadmap, full analysis history list, profile/settings
- [ ] Dashboard score-trend chart (recharts is installed, backend data is ready)
- [ ] Redis caching layer for repeated analysis lookups
- [ ] Alembic migrations (currently using `create_all` for dev convenience)
- [ ] DB-driven skill taxonomy admin CRUD (table exists, not yet wired to an editor)
- [ ] "X or Y" requirement parsing in the JD analyzer (see Known Limitations)
