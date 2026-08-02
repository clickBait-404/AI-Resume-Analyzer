"""
Interview Question Generator.

Generates technical, behavioral, project-based, resume-based, and HR
interview questions for a given resume + target role.

Uses the live model when configured. The mock fallback uses a
curated question-template bank parameterized by the candidate's
actual detected skills and resume content (project names, company
names) — so even without a live model, questions reference real
specifics rather than being entirely generic.

Each question now also carries:
- why_this_matters: what the question is actually probing for
- sample_strong_answer_outline: the SHAPE of a strong answer (not a
  script to memorize, and never a fabricated achievement)
- red_flags: concrete weak-answer signals

...on top of the original expected_answer_points and
follow_up_question, so the output works as real interview prep
rather than a bare question list.
"""
import random

from ai.llm_client import get_structured_completion, is_live
from ai.prompt_manager import INTERVIEW_GENERATOR_SYSTEM_PROMPT, build_interview_generator_user_prompt
from ai.response_validator import validate_interview_questions

# Per-skill technical question templates. Covers the most common
# skills in the taxonomy; skills without a template fall back to a
# generic-but-still-skill-named question.
SKILL_QUESTION_TEMPLATES: dict[str, list[dict]] = {
    "Python": [
        {
            "question": "How does Python's GIL affect multi-threaded programs, and when would you reach for multiprocessing instead of threading?",
            "difficulty": "Medium",
            "why_this_matters": "Tests whether the candidate understands Python's concurrency model at a level deeper than 'just use threading', which is a common surface-level gap.",
            "expected_answer_points": [
                "Explains the GIL prevents true parallel execution of Python bytecode across threads",
                "Identifies multiprocessing as the right choice for CPU-bound work",
                "Notes threading is still useful for I/O-bound work despite the GIL",
            ],
            "sample_strong_answer_outline": "Opens by naming the GIL and what it actually restricts (one thread executing Python bytecode at a time), then splits the answer into CPU-bound vs I/O-bound work, explaining why multiprocessing sidesteps the GIL for the former while threading remains fine for the latter. Closes by mentioning asyncio as a third option for I/O-bound concurrency without the overhead of separate processes.",
            "red_flags": [
                "Claims Python threads run fully in parallel on multiple cores",
                "Can't distinguish when multiprocessing vs threading is the right call",
            ],
        },
    ],
    "FastAPI": [
        {
            "question": "How does FastAPI's dependency injection system work, and what's an example of where you'd use it?",
            "difficulty": "Medium",
            "why_this_matters": "Checks whether the candidate has actually used FastAPI's patterns in practice, versus just listing it as a resume keyword.",
            "expected_answer_points": [
                "Describes Depends() and how it injects shared logic into route handlers",
                "Gives a concrete example like a DB session or current-user auth check",
                "Mentions reusability/testability benefits",
            ],
            "sample_strong_answer_outline": "Starts by explaining Depends() as a way to declare reusable logic that FastAPI resolves and injects before the route handler runs, then gives one concrete real example (DB session or auth check) rather than a textbook definition, and closes on why this beats duplicating that logic in every route.",
            "red_flags": [
                "Can only describe it in the abstract with no concrete example",
                "Confuses dependency injection with simple function calls",
            ],
        },
    ],
    "React": [
        {
            "question": "Walk me through how you'd decide between useState, useReducer, and lifting state up in a React component tree.",
            "difficulty": "Medium",
            "why_this_matters": "Reveals whether the candidate has real judgment about state management decisions, not just familiarity with the hooks' syntax.",
            "expected_answer_points": [
                "useState for simple local state",
                "useReducer for complex state transitions with multiple sub-values",
                "Lifting state up when multiple components need to share it",
            ],
            "sample_strong_answer_outline": "Walks through the decision as a spectrum: useState for simple, independent values; useReducer once state transitions become interdependent or numerous; lifting state up specifically when sibling components need to share it. Ideally references a real case from their own project rather than a purely theoretical answer.",
            "red_flags": [
                "Treats all three as interchangeable with no real criteria",
                "No reference to an actual project where this decision came up",
            ],
        },
    ],
    "PostgreSQL": [
        {
            "question": "How would you diagnose a slow PostgreSQL query, and what tools would you use?",
            "difficulty": "Medium",
            "why_this_matters": "Separates candidates who've only used an ORM from those who've actually had to debug real database performance issues.",
            "expected_answer_points": [
                "Mentions EXPLAIN ANALYZE to inspect the query plan",
                "Discusses indexing strategy",
                "Considers N+1 query patterns if coming from an ORM",
            ],
            "sample_strong_answer_outline": "Leads with EXPLAIN ANALYZE as the starting point to see the actual query plan and where time is spent, then discusses indexing as the most common fix, and if they've used an ORM, mentions checking for N+1 query patterns as a frequent hidden cause of slowness.",
            "red_flags": [
                "Only suggests 'adding an index' without explaining how they'd identify where one is needed",
                "Has never heard of or used EXPLAIN ANALYZE",
            ],
        },
    ],
    "Docker": [
        {
            "question": "What's the difference between a Docker image and a container, and how do you keep image sizes small?",
            "difficulty": "Easy",
            "why_this_matters": "A baseline check that the candidate understands Docker fundamentals rather than just having copy-pasted a Dockerfile once.",
            "expected_answer_points": [
                "Image is the immutable template, container is a running instance",
                "Mentions multi-stage builds or slim base images",
                "Mentions .dockerignore or layer caching",
            ],
            "sample_strong_answer_outline": "Defines image vs container clearly (template vs running instance), then gives at least one concrete size-reduction technique they've actually used — multi-stage builds, a slim/alpine base image, or .dockerignore — rather than listing all of them generically.",
            "red_flags": [
                "Uses 'image' and 'container' interchangeably",
                "Has no concrete technique for reducing image size, only vague awareness",
            ],
        },
    ],
    "AWS": [
        {
            "question": "If you needed to deploy a containerized API with auto-scaling on AWS, what services would you reach for and why?",
            "difficulty": "Medium",
            "why_this_matters": "Tests whether AWS on the resume reflects real architectural understanding or just exposure to the console.",
            "expected_answer_points": [
                "Names a relevant compute service (ECS/EKS/Fargate)",
                "Mentions a load balancer (ALB)",
                "Touches on auto-scaling configuration basics",
            ],
            "sample_strong_answer_outline": "Names a specific compute option (ECS/Fargate is the simplest defensible answer for most candidates), explains why it fits a containerized workload, adds an ALB for traffic distribution, and briefly touches on what triggers auto-scaling (CPU/memory thresholds or request count).",
            "red_flags": [
                "Lists AWS service names with no explanation of why each is needed",
                "Can't explain what triggers auto-scaling at even a basic level",
            ],
        },
    ],
    "REST API": [
        {
            "question": "What makes an API 'RESTful', and what's a REST design decision you've had to make in a project?",
            "difficulty": "Easy",
            "why_this_matters": "Confirms the candidate can apply REST principles in practice, not just recite the acronym.",
            "expected_answer_points": [
                "References resource-based URLs, statelessness, standard HTTP verbs",
                "Gives a concrete example from their own experience",
            ],
            "sample_strong_answer_outline": "Briefly defines RESTful design (resource-oriented URLs, standard HTTP verbs, statelessness), then pivots quickly to a real design decision from their own project — e.g. how they structured nested resources or chose status codes — rather than staying purely theoretical.",
            "red_flags": [
                "Can define REST in the abstract but has no real example from their own work",
            ],
        },
    ],
}

GENERIC_TECHNICAL_FALLBACK = {
    "question": "Tell me about your hands-on experience with {skill} — what's something non-trivial you built or solved with it?",
    "difficulty": "Medium",
    "why_this_matters": "Distinguishes candidates who've genuinely used {skill} from those who listed it after a single tutorial.",
    "expected_answer_points": [
        "Gives a specific, non-generic example rather than a textbook definition",
        "Explains a real decision or tradeoff they made",
    ],
    "sample_strong_answer_outline": "Names one specific thing they built or solved with {skill}, explains a real decision or tradeoff involved, and avoids generic statements like 'I used it for a project' with no further detail.",
    "red_flags": [
        "Can't name a specific example, only describes {skill} in general terms",
    ],
}

BEHAVIORAL_BANK = [
    {
        "question": "Tell me about a time you disagreed with a technical decision made by your team. What did you do?",
        "difficulty": "Medium",
        "why_this_matters": "Assesses how the candidate handles conflict and whether they can advocate for a position professionally without being either a pushover or combative.",
        "expected_answer_points": [
            "Describes the disagreement specifically, not vaguely",
            "Shows they advocated for their view with reasoning, not just deference or stubbornness",
            "Describes the actual outcome, including if they were wrong",
        ],
        "sample_strong_answer_outline": "Names a specific, real disagreement (not a hypothetical), explains the reasoning behind their position, describes how they raised it with the team, and honestly states the outcome — including admitting if the team's original decision turned out to be right.",
        "red_flags": [
            "Answer is entirely hypothetical or vague ('sometimes I disagree, but I usually go with the team')",
            "Frames themselves as always right with no acknowledgment of the other side's reasoning",
        ],
    },
    {
        "question": "Describe a project that didn't go as planned. What happened, and what would you do differently?",
        "difficulty": "Medium",
        "why_this_matters": "Reveals whether the candidate can own failure honestly and extract a real lesson, rather than deflecting blame.",
        "expected_answer_points": [
            "Owns their part in what went wrong rather than only blaming external factors",
            "Shows concrete learning, not just a vague 'I learned a lot'",
        ],
        "sample_strong_answer_outline": "Describes a specific project and what concretely went wrong, takes ownership of their own role in it rather than only citing external factors, and names one specific thing they'd do differently next time.",
        "red_flags": [
            "Blames only other people, tools, or circumstances with no self-reflection",
            "'What I'd do differently' answer is vague ('be more careful') rather than specific",
        ],
    },
    {
        "question": "Tell me about a time you had to learn a new technology quickly to get something done.",
        "difficulty": "Easy",
        "why_this_matters": "Checks for real evidence of fast, self-directed learning, which matters heavily for a role with a fast-moving stack.",
        "expected_answer_points": [
            "Describes a real time-constrained learning situation",
            "Explains how they approached learning efficiently",
        ],
        "sample_strong_answer_outline": "Names the specific technology and the deadline pressure, describes their actual learning approach (docs, a specific course, trial-and-error on a small piece first), and ties it back to a concrete outcome they delivered.",
        "red_flags": [
            "No specific technology or timeframe named, just generic 'I'm a fast learner' framing",
        ],
    },
]

HR_BANK = [
    {
        "question": "Why are you interested in this specific role, beyond it being a job opening?",
        "difficulty": "Easy",
        "why_this_matters": "Filters out candidates applying indiscriminately from those who've actually thought about fit with this specific role and company.",
        "expected_answer_points": [
            "References something specific about the role or company, not generic enthusiasm",
        ],
        "sample_strong_answer_outline": "Names something specific about the role, team, or company's problem space that genuinely connects to the candidate's own background or interests, rather than a generic 'I want to grow and learn' answer.",
        "red_flags": [
            "Answer is entirely generic and could be copy-pasted into any application",
        ],
    },
    {
        "question": "Where do you see yourself technically in 2-3 years?",
        "difficulty": "Easy",
        "why_this_matters": "Gauges whether the candidate's growth direction is realistic and roughly compatible with what this role can actually offer.",
        "expected_answer_points": [
            "Shows some direction without being unrealistic or disconnected from the role",
        ],
        "sample_strong_answer_outline": "Describes a realistic, specific direction (e.g. deepening in a particular area, or moving toward more ownership/design responsibility) that plausibly builds on what this role offers, rather than an unrelated or wildly ambitious claim.",
        "red_flags": [
            "Stated goal has no realistic connection to what this role could offer",
        ],
    },
    {
        "question": "What's your ideal team environment, and how do you handle working with people whose style differs from yours?",
        "difficulty": "Easy",
        "why_this_matters": "Surfaces self-awareness about working style and whether the candidate can adapt rather than just wanting everyone to match their preference.",
        "expected_answer_points": [
            "Shows self-awareness about their own working style",
            "Gives a concrete example of adapting to someone different",
        ],
        "sample_strong_answer_outline": "Names a real working-style preference honestly, then gives one concrete example of successfully adapting to work with someone whose style differed, rather than claiming to get along with everyone effortlessly.",
        "red_flags": [
            "Claims to have no preferences and get along with literally everyone with no example",
        ],
    },
]


def _build_mock_questions(parsed_resume: dict) -> dict:
    skills = parsed_resume.get("skills", [])
    projects = parsed_resume.get("projects", [])
    experience = parsed_resume.get("experience", [])

    questions = []

    # Technical: pull from template bank for up to 2 of the candidate's
    # actual skills, falling back to a parameterized generic template.
    technical_skills = [s for s in skills if s in SKILL_QUESTION_TEMPLATES][:2]
    if not technical_skills and skills:
        technical_skills = skills[:2]

    for skill in technical_skills:
        if skill in SKILL_QUESTION_TEMPLATES:
            template = random.choice(SKILL_QUESTION_TEMPLATES[skill])
            questions.append({
                "category": "Technical",
                "question": template["question"],
                "difficulty": template["difficulty"],
                "why_this_matters": template["why_this_matters"],
                "expected_answer_points": template["expected_answer_points"],
                "sample_strong_answer_outline": template["sample_strong_answer_outline"],
                "red_flags": template["red_flags"],
                "follow_up_question": f"Can you walk through a specific example from your own experience with {skill}?",
            })
        else:
            questions.append({
                "category": "Technical",
                "question": GENERIC_TECHNICAL_FALLBACK["question"].format(skill=skill),
                "difficulty": GENERIC_TECHNICAL_FALLBACK["difficulty"],
                "why_this_matters": GENERIC_TECHNICAL_FALLBACK["why_this_matters"].format(skill=skill),
                "expected_answer_points": GENERIC_TECHNICAL_FALLBACK["expected_answer_points"],
                "sample_strong_answer_outline": GENERIC_TECHNICAL_FALLBACK["sample_strong_answer_outline"].format(skill=skill),
                "red_flags": [r.format(skill=skill) for r in GENERIC_TECHNICAL_FALLBACK["red_flags"]],
                "follow_up_question": f"What would you do differently if you used {skill} on this again?",
            })

    # Pad technical to at least 2 if the resume listed fewer than 2 skills.
    while len([q for q in questions if q["category"] == "Technical"]) < 2:
        questions.append({
            "category": "Technical",
            "question": "Walk me through how you'd design a basic CRUD API for a new resource, from request to database.",
            "difficulty": "Easy",
            "why_this_matters": "A baseline check that the candidate can reason through a full request lifecycle, not just isolated snippets.",
            "expected_answer_points": ["Covers routing, validation, persistence layer, and response shape"],
            "sample_strong_answer_outline": "Walks through the flow in order: route/endpoint definition, input validation, the persistence layer call, and the response shape returned — touching each stage rather than jumping straight to the database.",
            "red_flags": ["Skips validation or error handling entirely when walking through the design"],
            "follow_up_question": "How would you add authentication to this?",
        })

    # Project-Based: reference actual project names if present.
    for project in projects[:2]:
        name = project.get("name") or "one of your projects"
        questions.append({
            "category": "Project-Based",
            "question": f"Walk me through the architecture of '{name}'. What was the hardest technical decision you made building it?",
            "difficulty": "Medium",
            "why_this_matters": f"Tests whether the candidate can speak to '{name}' with real depth, versus only what's written in the resume bullet.",
            "expected_answer_points": [
                "Describes the actual architecture, not just a feature list",
                "Identifies a real tradeoff or decision point",
            ],
            "sample_strong_answer_outline": f"Describes '{name}'s architecture at a system level (major components and how they connect), then focuses on one specific hard decision — a tradeoff between two real options — rather than just listing features that were built.",
            "red_flags": [
                "Only lists features/tech used with no explanation of how components connect",
                "Can't identify a single real tradeoff or difficult decision",
            ],
            "follow_up_question": f"What would you change about '{name}' if you rebuilt it today?",
        })
    while len([q for q in questions if q["category"] == "Project-Based"]) < 2:
        questions.append({
            "category": "Project-Based",
            "question": "Tell me about the most technically challenging project you've worked on.",
            "difficulty": "Medium",
            "why_this_matters": "Gives the candidate room to show depth on whatever they consider their strongest work.",
            "expected_answer_points": ["Identifies genuine complexity, not just scope or size"],
            "sample_strong_answer_outline": "Names the project and pinpoints exactly what made it hard technically (not just time-consuming), then walks through how they approached solving that specific difficulty.",
            "red_flags": ["Describes a large project without identifying what specifically was technically hard about it"],
            "follow_up_question": "What was the single hardest bug you had to fix in it?",
        })

    # Resume-Based: reference actual company/role if present.
    for exp in experience[:2]:
        company = exp.get("company") or "your previous role"
        title = exp.get("title") or "that position"
        questions.append({
            "category": "Resume-Based",
            "question": f"Your resume mentions {title} at {company}. What was your specific day-to-day contribution there, beyond the bullet points?",
            "difficulty": "Easy",
            "why_this_matters": f"Checks that the {title} experience at {company} reflects real, specific work rather than an inflated resume line.",
            "expected_answer_points": ["Gives specifics beyond what's already written on the resume"],
            "sample_strong_answer_outline": f"Adds concrete, day-to-day detail about the {title} role at {company} that isn't already captured in the resume bullet — specific tasks, tools used regularly, or how their work fit into the wider team.",
            "red_flags": ["Simply re-reads the resume bullet back with no additional detail"],
            "follow_up_question": f"What's something you'd want a future employer to know about your time at {company} that isn't on the resume?",
        })
    while len([q for q in questions if q["category"] == "Resume-Based"]) < 2:
        questions.append({
            "category": "Resume-Based",
            "question": "Walk me through your resume from top to bottom, in your own words.",
            "difficulty": "Easy",
            "why_this_matters": "A classic opener that reveals how clearly the candidate can narrate their own background under light pressure.",
            "expected_answer_points": ["Tells a coherent narrative, not just a re-read of the resume"],
            "sample_strong_answer_outline": "Tells a coherent, chronological story connecting the major items on the resume, rather than reading them off in isolation, and lands on what led them to be interested in this role.",
            "red_flags": ["Reads the resume back verbatim with no narrative connecting the pieces"],
            "follow_up_question": "What's the one item on here you're most proud of, and why?",
        })

    # Behavioral and HR from the static banks (already carry the full
    # upgraded schema).
    questions.extend([{**q, "category": "Behavioral", "follow_up_question": "What would you do differently next time?"} for q in random.sample(BEHAVIORAL_BANK, k=2)])
    questions.extend([{**q, "category": "HR", "follow_up_question": "What questions do you have for us?"} for q in random.sample(HR_BANK, k=2)])

    # Ensure a real difficulty spread even in the mock path: bump one
    # Technical or Project-Based question to Hard if none exists yet,
    # mirroring the rule given to the live prompt.
    if not any(q["difficulty"] == "Hard" for q in questions):
        for q in questions:
            if q["category"] in ("Technical", "Project-Based"):
                q["difficulty"] = "Hard"
                break

    return {"questions": questions, "source": "mock_fallback"}


def generate_interview_questions(resume_raw_text: str, jd_raw_text: str, parsed_resume: dict) -> dict:
    if is_live():
        user_prompt = build_interview_generator_user_prompt(resume_raw_text, jd_raw_text)
        result = get_structured_completion(INTERVIEW_GENERATOR_SYSTEM_PROMPT, user_prompt)
        if result and validate_interview_questions(result):
            result["source"] = "openai"
            return result

    return _build_mock_questions(parsed_resume)