"""
Interview Question Generator.

Generates technical, behavioral, project-based, resume-based, and HR
interview questions for a given resume + target role.

Uses OpenAI when configured. The mock fallback uses a curated
question-template bank parameterized by the candidate's actual
detected skills and resume content (project names, company names) —
so even without a live model, questions reference real specifics
rather than being entirely generic.
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
            "expected_answer_points": [
                "Explains the GIL prevents true parallel execution of Python bytecode across threads",
                "Identifies multiprocessing as the right choice for CPU-bound work",
                "Notes threading is still useful for I/O-bound work despite the GIL",
            ],
        },
    ],
    "FastAPI": [
        {
            "question": "How does FastAPI's dependency injection system work, and what's an example of where you'd use it?",
            "difficulty": "Medium",
            "expected_answer_points": [
                "Describes Depends() and how it injects shared logic into route handlers",
                "Gives a concrete example like a DB session or current-user auth check",
                "Mentions reusability/testability benefits",
            ],
        },
    ],
    "React": [
        {
            "question": "Walk me through how you'd decide between useState, useReducer, and lifting state up in a React component tree.",
            "difficulty": "Medium",
            "expected_answer_points": [
                "useState for simple local state",
                "useReducer for complex state transitions with multiple sub-values",
                "Lifting state up when multiple components need to share it",
            ],
        },
    ],
    "PostgreSQL": [
        {
            "question": "How would you diagnose a slow PostgreSQL query, and what tools would you use?",
            "difficulty": "Medium",
            "expected_answer_points": [
                "Mentions EXPLAIN ANALYZE to inspect the query plan",
                "Discusses indexing strategy",
                "Considers N+1 query patterns if coming from an ORM",
            ],
        },
    ],
    "Docker": [
        {
            "question": "What's the difference between a Docker image and a container, and how do you keep image sizes small?",
            "difficulty": "Easy",
            "expected_answer_points": [
                "Image is the immutable template, container is a running instance",
                "Mentions multi-stage builds or slim base images",
                "Mentions .dockerignore or layer caching",
            ],
        },
    ],
    "AWS": [
        {
            "question": "If you needed to deploy a containerized API with auto-scaling on AWS, what services would you reach for and why?",
            "difficulty": "Medium",
            "expected_answer_points": [
                "Names a relevant compute service (ECS/EKS/Fargate)",
                "Mentions a load balancer (ALB)",
                "Touches on auto-scaling configuration basics",
            ],
        },
    ],
    "REST API": [
        {
            "question": "What makes an API 'RESTful', and what's a REST design decision you've had to make in a project?",
            "difficulty": "Easy",
            "expected_answer_points": [
                "References resource-based URLs, statelessness, standard HTTP verbs",
                "Gives a concrete example from their own experience",
            ],
        },
    ],
}

GENERIC_TECHNICAL_FALLBACK = {
    "question": "Tell me about your hands-on experience with {skill} — what's something non-trivial you built or solved with it?",
    "difficulty": "Medium",
    "expected_answer_points": [
        "Gives a specific, non-generic example rather than a textbook definition",
        "Explains a real decision or tradeoff they made",
    ],
}

BEHAVIORAL_BANK = [
    {
        "question": "Tell me about a time you disagreed with a technical decision made by your team. What did you do?",
        "difficulty": "Medium",
        "expected_answer_points": [
            "Describes the disagreement specifically, not vaguely",
            "Shows they advocated for their view with reasoning, not just deference or stubbornness",
            "Describes the actual outcome, including if they were wrong",
        ],
    },
    {
        "question": "Describe a project that didn't go as planned. What happened, and what would you do differently?",
        "difficulty": "Medium",
        "expected_answer_points": [
            "Owns their part in what went wrong rather than only blaming external factors",
            "Shows concrete learning, not just a vague 'I learned a lot'",
        ],
    },
    {
        "question": "Tell me about a time you had to learn a new technology quickly to get something done.",
        "difficulty": "Easy",
        "expected_answer_points": [
            "Describes a real time-constrained learning situation",
            "Explains how they approached learning efficiently",
        ],
    },
]

HR_BANK = [
    {
        "question": "Why are you interested in this specific role, beyond it being a job opening?",
        "difficulty": "Easy",
        "expected_answer_points": [
            "References something specific about the role or company, not generic enthusiasm",
        ],
    },
    {
        "question": "Where do you see yourself technically in 2-3 years?",
        "difficulty": "Easy",
        "expected_answer_points": [
            "Shows some direction without being unrealistic or disconnected from the role",
        ],
    },
    {
        "question": "What's your ideal team environment, and how do you handle working with people whose style differs from yours?",
        "difficulty": "Easy",
        "expected_answer_points": [
            "Shows self-awareness about their own working style",
            "Gives a concrete example of adapting to someone different",
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
                "expected_answer_points": template["expected_answer_points"],
                "follow_up_question": f"Can you walk through a specific example from your own experience with {skill}?",
            })
        else:
            questions.append({
                "category": "Technical",
                "question": GENERIC_TECHNICAL_FALLBACK["question"].format(skill=skill),
                "difficulty": GENERIC_TECHNICAL_FALLBACK["difficulty"],
                "expected_answer_points": GENERIC_TECHNICAL_FALLBACK["expected_answer_points"],
                "follow_up_question": f"What would you do differently if you used {skill} on this again?",
            })

    # Pad technical to at least 2 if the resume listed fewer than 2 skills.
    while len([q for q in questions if q["category"] == "Technical"]) < 2:
        questions.append({
            "category": "Technical",
            "question": "Walk me through how you'd design a basic CRUD API for a new resource, from request to database.",
            "difficulty": "Easy",
            "expected_answer_points": ["Covers routing, validation, persistence layer, and response shape"],
            "follow_up_question": "How would you add authentication to this?",
        })

    # Project-Based: reference actual project names if present.
    for project in projects[:2]:
        name = project.get("name") or "one of your projects"
        questions.append({
            "category": "Project-Based",
            "question": f"Walk me through the architecture of '{name}'. What was the hardest technical decision you made building it?",
            "difficulty": "Medium",
            "expected_answer_points": [
                "Describes the actual architecture, not just a feature list",
                "Identifies a real tradeoff or decision point",
            ],
            "follow_up_question": f"What would you change about '{name}' if you rebuilt it today?",
        })
    while len([q for q in questions if q["category"] == "Project-Based"]) < 2:
        questions.append({
            "category": "Project-Based",
            "question": "Tell me about the most technically challenging project you've worked on.",
            "difficulty": "Medium",
            "expected_answer_points": ["Identifies genuine complexity, not just scope or size"],
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
            "expected_answer_points": ["Gives specifics beyond what's already written on the resume"],
            "follow_up_question": f"What's something you'd want a future employer to know about your time at {company} that isn't on the resume?",
        })
    while len([q for q in questions if q["category"] == "Resume-Based"]) < 2:
        questions.append({
            "category": "Resume-Based",
            "question": "Walk me through your resume from top to bottom, in your own words.",
            "difficulty": "Easy",
            "expected_answer_points": ["Tells a coherent narrative, not just a re-read of the resume"],
            "follow_up_question": "What's the one item on here you're most proud of, and why?",
        })

    # Behavioral and HR from the static banks.
    questions.extend([{**q, "category": "Behavioral", "follow_up_question": "What would you do differently next time?"} for q in random.sample(BEHAVIORAL_BANK, k=2)])
    questions.extend([{**q, "category": "HR", "follow_up_question": "What questions do you have for us?"} for q in random.sample(HR_BANK, k=2)])

    return {"questions": questions, "source": "mock_fallback"}


def generate_interview_questions(resume_raw_text: str, jd_raw_text: str, parsed_resume: dict) -> dict:
    if is_live():
        user_prompt = build_interview_generator_user_prompt(resume_raw_text, jd_raw_text)
        result = get_structured_completion(INTERVIEW_GENERATOR_SYSTEM_PROMPT, user_prompt)
        if result and validate_interview_questions(result):
            result["source"] = "openai"
            return result

    return _build_mock_questions(parsed_resume)
