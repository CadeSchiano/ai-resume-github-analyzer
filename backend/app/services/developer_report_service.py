"""Assemble deterministic developer-readiness evidence from resume and GitHub data."""

from typing import Any

from app.services.cross_analysis_service import compare_resume_skills
from app.services.report_service import generate_report
from app.services.resume_report_service import generate_resume_report


def generate_developer_report(username: str, resume_text: str) -> dict[str, Any] | None:
    """Combine existing Phase 1 and Phase 2 reports with skill evidence mapping."""
    github_analysis = generate_report(username)
    if github_analysis is None:
        return None

    resume_analysis = generate_resume_report(resume_text)
    return {
        "username": username,
        "github_analysis": github_analysis,
        "resume_analysis": resume_analysis,
        "resume_github_evidence": compare_resume_skills(
            resume_analysis["skills"], github_analysis["repositories"]
        ),
    }
