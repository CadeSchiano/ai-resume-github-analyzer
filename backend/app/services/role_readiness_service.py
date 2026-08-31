"""Deterministic target-role readiness scoring from resume and GitHub evidence."""

from typing import Any


ROLE_REQUIREMENTS = {
    "Software Engineer Intern": (
        ("programming language", {"Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust"}),
        ("application technology", {"React", "Node.js", "FastAPI", "Django", "Flask", "Spring", "REST APIs"}),
    ),
    "Software Engineer": (
        ("programming language", {"Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust"}),
        ("application technology", {"React", "Node.js", "FastAPI", "Django", "Flask", "Spring", "REST APIs", "GraphQL"}),
        ("data or deployment technology", {"PostgreSQL", "MySQL", "MongoDB", "Docker", "AWS", "Azure"}),
    ),
    "Backend Developer": (
        ("backend language", {"Python", "Java", "Go", "C#", "Node.js"}),
        ("API technology", {"REST APIs", "GraphQL", "FastAPI", "Django", "Flask", "Express", "Spring"}),
        ("database technology", {"PostgreSQL", "MySQL", "MongoDB", "Redis"}),
    ),
    "Frontend Developer": (
        ("web language", {"JavaScript", "TypeScript"}),
        ("frontend framework", {"React", "Next.js", "Vue", "Angular"}),
    ),
    "Full-Stack Developer": (
        ("web language", {"JavaScript", "TypeScript"}),
        ("frontend framework", {"React", "Next.js", "Vue", "Angular"}),
        ("backend technology", {"Node.js", "Python", "FastAPI", "Django", "Flask", "Express", "Spring", "REST APIs"}),
        ("database technology", {"PostgreSQL", "MySQL", "MongoDB", "Redis"}),
    ),
    "Mobile Developer": (
        ("mobile language", {"Swift", "Kotlin", "Dart", "JavaScript", "TypeScript"}),
        ("mobile framework or platform", {"React Native", "Flutter", "Android", "iOS"}),
    ),
    "AI/ML": (
        ("programming language", {"Python"}),
        ("machine-learning technology", {"TensorFlow", "PyTorch", "scikit-learn", "NumPy", "pandas"}),
    ),
}
RESUME_CLAIM_WEIGHT = 45
PUBLIC_EVIDENCE_WEIGHT = 35
PROJECT_EVIDENCE_WEIGHT = 20
EVIDENCE_POINTS = {
    "strong_public_evidence": 1,
    "some_public_evidence": 20 / 35,
    "no_public_github_evidence_found": 0,
}


def supported_roles() -> list[str]:
    return list(ROLE_REQUIREMENTS)


def calculate_role_readiness(
    target_role: str,
    resume_skills: list[str],
    skill_evidence: list[dict[str, Any]],
    has_projects: bool,
) -> dict[str, Any]:
    """Score fit for one supported role without inferring unlisted skills."""
    if target_role not in ROLE_REQUIREMENTS:
        raise ValueError(f"Unsupported target role: {target_role}")

    resume_skill_set = set(resume_skills)
    evidence_by_skill = {item["skill"]: item["evidence_level"] for item in skill_evidence}
    requirement_results = []

    for label, accepted_skills in ROLE_REQUIREMENTS[target_role]:
        matched_skills = sorted(resume_skill_set & accepted_skills)
        evidence_levels = [evidence_by_skill.get(skill, "no_public_github_evidence_found") for skill in matched_skills]
        if "strong_public_evidence" in evidence_levels:
            public_evidence = "strong_public_evidence"
        elif "some_public_evidence" in evidence_levels:
            public_evidence = "some_public_evidence"
        else:
            public_evidence = "no_public_github_evidence_found"
        requirement_results.append(
            {
                "requirement": label,
                "matched_resume_skills": matched_skills,
                "public_evidence": public_evidence,
            }
        )

    requirement_count = len(requirement_results)
    resume_claim_score = round(
        RESUME_CLAIM_WEIGHT
        * sum(bool(item["matched_resume_skills"]) for item in requirement_results)
        / requirement_count
    )
    public_evidence_score = round(
        PUBLIC_EVIDENCE_WEIGHT
        * sum(EVIDENCE_POINTS[item["public_evidence"]] for item in requirement_results)
        / requirement_count
    )
    categories = {
        "resume_skill_alignment": resume_claim_score,
        "public_github_evidence": public_evidence_score,
        "project_evidence": PROJECT_EVIDENCE_WEIGHT if has_projects else 0,
    }
    return {
        "target_role": target_role,
        "role_readiness_score": sum(categories.values()),
        "categories": categories,
        "requirements": requirement_results,
    }
