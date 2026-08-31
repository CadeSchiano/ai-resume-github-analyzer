"""Deterministic scoring for parsed resume evidence."""

import re
from typing import Any

from app.services.resume_parser_service import SKILL_PATTERNS


CATEGORY_WEIGHTS = {
    "technical_skills": 30,
    "experience": 30,
    "projects": 30,
    "structure": 10,
}
SKILL_DOMAINS = {
    "Python": "language",
    "JavaScript": "language",
    "TypeScript": "language",
    "Java": "language",
    "C++": "language",
    "C#": "language",
    "Swift": "language",
    "Kotlin": "language",
    "Dart": "language",
    "Go": "language",
    "Rust": "language",
    "SQL": "language",
    "React": "framework",
    "React Native": "framework",
    "Next.js": "framework",
    "Vue": "framework",
    "Angular": "framework",
    "Flutter": "framework",
    "Android": "mobile",
    "iOS": "mobile",
    "Node.js": "framework",
    "Express": "framework",
    "Django": "framework",
    "Flask": "framework",
    "FastAPI": "framework",
    "Spring": "framework",
    "PostgreSQL": "database",
    "MySQL": "database",
    "MongoDB": "database",
    "Redis": "database",
    "Docker": "deployment",
    "Kubernetes": "deployment",
    "AWS": "cloud",
    "Azure": "cloud",
    "Git": "tooling",
    "GitHub": "tooling",
    "Linux": "tooling",
    "REST APIs": "api",
    "GraphQL": "api",
    "TensorFlow": "machine_learning",
    "PyTorch": "machine_learning",
    "NumPy": "machine_learning",
    "pandas": "machine_learning",
    "scikit-learn": "machine_learning",
}
ACTION_PATTERN = re.compile(
    r"\b(built|created|developed|designed|implemented|improved|optimized|led|deployed|automated|integrated|tested)\b",
    re.IGNORECASE,
)
OUTCOME_PATTERN = re.compile(r"\b\d+(?:\.\d+)?(?:%|x\b| users\b| ms\b| seconds\b| hours\b| requests\b)", re.IGNORECASE)


def _combined_text(entries: list[str]) -> str:
    return "\n".join(entries)


def _contains_technical_skill(text: str) -> bool:
    normalized_text = text.casefold()
    return any(re.search(pattern, normalized_text) for pattern in SKILL_PATTERNS.values())


def _skills_score(parsed_resume: dict[str, Any]) -> int:
    skills = parsed_resume.get("skills", [])
    domains = {SKILL_DOMAINS[skill] for skill in skills if skill in SKILL_DOMAINS}
    has_skills_section = bool(parsed_resume.get("sections", {}).get("skills"))
    return min(len(skills) * 4, 16) + min(len(domains) * 2, 8) + (6 if has_skills_section else 0)


def _evidence_score(entries: list[str]) -> int:
    text = _combined_text(entries)
    return (
        min(len(entries) * 5, 10)
        + (10 if ACTION_PATTERN.search(text) else 0)
        + (10 if OUTCOME_PATTERN.search(text) else 0)
    )


def _projects_score(entries: list[str]) -> int:
    text = _combined_text(entries)
    return (
        min(len(entries) * 5, 5)
        + (10 if _contains_technical_skill(text) else 0)
        + (10 if ACTION_PATTERN.search(text) else 0)
        + (5 if OUTCOME_PATTERN.search(text) else 0)
    )


def _structure_score(parsed_resume: dict[str, Any]) -> int:
    sections = parsed_resume.get("sections", {})
    core_sections = ("skills", "experience", "projects", "education")
    return sum(2 for section in core_sections if sections.get(section)) + (2 if sections.get("summary") else 0)


def calculate_resume_scores(parsed_resume: dict[str, Any]) -> dict[str, Any]:
    """Calculate a resume evidence score without inferring capability or seniority."""
    categories = {
        "technical_skills": _skills_score(parsed_resume),
        "experience": _evidence_score(parsed_resume.get("experience", [])),
        "projects": _projects_score(parsed_resume.get("projects", [])),
        "structure": _structure_score(parsed_resume),
    }
    return {
        "resume_score": sum(categories.values()),
        "categories": categories,
    }
