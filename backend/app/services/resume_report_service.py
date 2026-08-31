"""Assemble deterministic resume analysis results."""

import re
from typing import Any

from app.services.resume_parser_service import SKILL_PATTERNS, parse_resume_text
from app.services.resume_scoring_service import ACTION_PATTERN, OUTCOME_PATTERN, calculate_resume_scores


def _feedback(parsed_resume: dict[str, Any]) -> tuple[list[str], list[str]]:
    sections = parsed_resume["sections"]
    skills = parsed_resume["skills"]
    experience = parsed_resume["experience"]
    projects = parsed_resume["projects"]
    experience_text = "\n".join(experience)
    project_text = "\n".join(projects)
    strengths = []
    improvements = []

    if skills:
        strengths.append(f"Lists {len(skills)} explicitly named technical skill{'s' if len(skills) != 1 else ''}.")
    elif not sections.get("skills"):
        improvements.append("Add a dedicated Technical Skills section with the technologies you can discuss in an interview.")

    if experience:
        strengths.append(f"Includes {len(experience)} experience entr{'ies' if len(experience) != 1 else 'y'}.")
        if ACTION_PATTERN.search(experience_text):
            strengths.append("Experience entries use action-oriented language.")
        else:
            improvements.append("Start experience bullets with specific action verbs such as Built, Implemented, or Improved.")
        if not OUTCOME_PATTERN.search(experience_text):
            improvements.append("Quantify experience impact where accurate, such as performance gains, users served, or time saved.")
    else:
        improvements.append("Add relevant work, internship, research, leadership, or volunteer experience when available.")

    if projects:
        strengths.append(f"Includes {len(projects)} project entr{'ies' if len(projects) != 1 else 'y'}.")
        has_project_technology = any(
            re.search(pattern, project_text.casefold()) for pattern in SKILL_PATTERNS.values()
        )
        if not has_project_technology:
            improvements.append("Name the technologies used in each project so the technical work is clear.")
        if not ACTION_PATTERN.search(project_text):
            improvements.append("Describe what you built or implemented in each project, not only the project title.")
        if not OUTCOME_PATTERN.search(project_text):
            improvements.append("Add accurate project outcomes, scale, or performance details where available.")
    else:
        improvements.append("Add one or two projects that demonstrate the technical work you want employers to evaluate.")

    if not sections.get("education"):
        improvements.append("Add an Education section with your degree, program, or relevant training.")

    return strengths, improvements


def generate_resume_report(text: str) -> dict[str, Any]:
    """Generate a complete deterministic resume analysis from extracted text."""
    parsed_resume = parse_resume_text(text)
    strengths, improvements = _feedback(parsed_resume)

    return {
        **calculate_resume_scores(parsed_resume),
        "skills": parsed_resume["skills"],
        "experience": parsed_resume["experience"],
        "projects": parsed_resume["projects"],
        "strengths": strengths,
        "improvements": improvements,
    }
