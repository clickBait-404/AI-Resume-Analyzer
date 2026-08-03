"""
Canonical skill taxonomy used by the rule-based skill extraction
and matching engine. Each entry maps a canonical name to a category
and a list of aliases/variants that should resolve to it.

This is intentionally a Python data file (not hardcoded in services)
so it can be extended or eventually moved into the `skills` DB table
without changing any matching logic.

IMPORTANT: aliases must not be ordinary English words on their own
(e.g. "rest", "restful", "go") — the extractor does exact word-boundary
matching, so a bare common word will false-positive on unrelated text
like "the rest of the team" or "go over the requirements". Prefer
multi-word or clearly technical-only aliases. See skill_extractor.py
for the matching logic and its plural-handling behavior.
"""

SKILL_TAXONOMY: list[dict] = [
    # Languages
    {"canonical_name": "Python", "category": "language", "aliases": ["python", "python3", "py"]},
    {"canonical_name": "JavaScript", "category": "language", "aliases": ["javascript", "ecmascript"]},
    {"canonical_name": "TypeScript", "category": "language", "aliases": ["typescript", "ts"]},
    {"canonical_name": "Java", "category": "language", "aliases": ["java"]},
    {"canonical_name": "C++", "category": "language", "aliases": ["c++", "cpp"]},
    {"canonical_name": "C#", "category": "language", "aliases": ["c#", "csharp", "c sharp"]},
    # NOTE: bare "go" removed — it's a common English word ("go over",
    # "go live") and would false-positive on any resume/JD containing it.
    # This means a resume that says only "Go" (not "GoLang") for the
    # language won't be detected. If you want that covered, the safer
    # option is a case-sensitive, whole-word-only check for capital "Go"
    # done separately from this generic case-insensitive engine, not a
    # bare alias here.
    {"canonical_name": "Go", "category": "language", "aliases": ["golang"]},
    {"canonical_name": "Rust", "category": "language", "aliases": ["rust"]},
    {"canonical_name": "SQL", "category": "language", "aliases": ["sql"]},
    {"canonical_name": "C", "category": "language", "aliases": ["c programming", "c language"]},
    {"canonical_name": "PHP", "category": "language", "aliases": ["php"]},
    {"canonical_name": "Ruby", "category": "language", "aliases": ["ruby"]},
    {"canonical_name": "Kotlin", "category": "language", "aliases": ["kotlin"]},
    {"canonical_name": "Swift", "category": "language", "aliases": ["swift"]},

    # Frontend frameworks
    {"canonical_name": "React", "category": "framework", "aliases": ["react", "react.js", "reactjs"]},
    {"canonical_name": "Vue.js", "category": "framework", "aliases": ["vue", "vue.js", "vuejs"]},
    {"canonical_name": "Angular", "category": "framework", "aliases": ["angular", "angularjs"]},
    {"canonical_name": "Next.js", "category": "framework", "aliases": ["next.js", "nextjs"]},
    {"canonical_name": "Tailwind CSS", "category": "framework", "aliases": ["tailwind", "tailwindcss", "tailwind css"]},
    {"canonical_name": "Redux", "category": "framework", "aliases": ["redux"]},

    # Backend frameworks
    {"canonical_name": "FastAPI", "category": "framework", "aliases": ["fastapi", "fast api"]},
    {"canonical_name": "Django", "category": "framework", "aliases": ["django"]},
    {"canonical_name": "Flask", "category": "framework", "aliases": ["flask"]},
    {"canonical_name": "Node.js", "category": "framework", "aliases": ["node.js", "nodejs", "node"]},
    {"canonical_name": "Express.js", "category": "framework", "aliases": ["express.js", "expressjs", "express"]},
    {"canonical_name": "Spring Boot", "category": "framework", "aliases": ["spring boot", "spring"]},
    {"canonical_name": ".NET", "category": "framework", "aliases": [".net", "dotnet", "asp.net"]},

    # Databases
    {"canonical_name": "PostgreSQL", "category": "database", "aliases": ["postgresql", "postgres", "psql"]},
    {"canonical_name": "MySQL", "category": "database", "aliases": ["mysql"]},
    {"canonical_name": "MongoDB", "category": "database", "aliases": ["mongodb", "mongo"]},
    {"canonical_name": "Redis", "category": "database", "aliases": ["redis"]},
    {"canonical_name": "SQLite", "category": "database", "aliases": ["sqlite"]},
    {"canonical_name": "Elasticsearch", "category": "database", "aliases": ["elasticsearch", "elastic search"]},

    # Cloud / DevOps
    {"canonical_name": "AWS", "category": "cloud", "aliases": ["aws", "amazon web services"]},
    {"canonical_name": "Azure", "category": "cloud", "aliases": ["azure", "microsoft azure"]},
    {"canonical_name": "GCP", "category": "cloud", "aliases": ["gcp", "google cloud", "google cloud platform"]},
    {"canonical_name": "Docker", "category": "tool", "aliases": ["docker"]},
    {"canonical_name": "Kubernetes", "category": "tool", "aliases": ["kubernetes", "k8s"]},
    {"canonical_name": "CI/CD", "category": "concept", "aliases": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment"]},
    {"canonical_name": "Git", "category": "tool", "aliases": ["git"]},
    {"canonical_name": "GitHub Actions", "category": "tool", "aliases": ["github actions"]},
    {"canonical_name": "Terraform", "category": "tool", "aliases": ["terraform"]},
    {"canonical_name": "Jenkins", "category": "tool", "aliases": ["jenkins"]},
    {"canonical_name": "Nginx", "category": "tool", "aliases": ["nginx"]},
    {"canonical_name": "Linux", "category": "tool", "aliases": ["linux", "unix"]},

    # APIs / Architecture
    # NOTE: bare "rest" and "restful" removed — both are ordinary English
    # words ("the rest of the team", "a restful weekend") and would
    # false-positive constantly. Only multi-word, unambiguous forms remain.
    # The extractor's optional trailing-"s" handling covers "REST APIs".
    {"canonical_name": "REST API", "category": "concept", "aliases": ["rest api", "restful api"]},
    {"canonical_name": "GraphQL", "category": "concept", "aliases": ["graphql"]},
    {"canonical_name": "Microservices", "category": "concept", "aliases": ["microservices", "microservice architecture"]},
    {"canonical_name": "System Design", "category": "concept", "aliases": ["system design"]},
    {"canonical_name": "OOP", "category": "concept", "aliases": ["oop", "object oriented programming", "object-oriented programming"]},

    # Data / AI
    {"canonical_name": "Machine Learning", "category": "concept", "aliases": ["machine learning", "ml"]},
    {"canonical_name": "Data Analysis", "category": "concept", "aliases": ["data analysis", "data analytics"]},
    {"canonical_name": "Pandas", "category": "tool", "aliases": ["pandas"]},
    {"canonical_name": "NumPy", "category": "tool", "aliases": ["numpy"]},

    # Testing
    {"canonical_name": "Unit Testing", "category": "concept", "aliases": ["unit testing", "unit tests"]},
    {"canonical_name": "Jest", "category": "tool", "aliases": ["jest"]},
    {"canonical_name": "Pytest", "category": "tool", "aliases": ["pytest"]},

    # Soft skills
    {"canonical_name": "Agile", "category": "concept", "aliases": ["agile", "scrum"]},
    {"canonical_name": "Communication", "category": "soft_skill", "aliases": ["communication skills", "communication"]},
    {"canonical_name": "Leadership", "category": "soft_skill", "aliases": ["leadership"]},
    {"canonical_name": "Problem Solving", "category": "soft_skill", "aliases": ["problem solving", "problem-solving"]},
    {"canonical_name": "Teamwork", "category": "soft_skill", "aliases": ["teamwork", "collaboration"]},
]