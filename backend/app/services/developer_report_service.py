"""Assemble deterministic developer-readiness evidence from resume and GitHub data."""

from typing import Any

from app.services.cross_analysis_service import compare_resume_skills
from app.services.report_service import generate_report
from app.services.resume_report_service import generate_resume_report
from app.services.role_readiness_service import calculate_role_readiness


def generate_developer_report(
    username: str, resume_text: str, target_role: str | None = None
) -> dict[str, Any] | None:
    """Combine existing Phase 1 and Phase 2 reports with skill evidence mapping."""
    github_analysis = generate_report(username)
    if github_analysis is None:
        return None

    resume_analysis = generate_resume_report(resume_text)
    report = {
        "username": username,
        "github_analysis": github_analysis,
        "resume_analysis": resume_analysis,
        "resume_github_evidence": compare_resume_skills(
            resume_analysis["skills"], github_analysis["repositories"]
        ),
    }
    if target_role:
        report["role_readiness"] = calculate_role_readiness(
            target_role,
            resume_analysis["skills"],
            report["resume_github_evidence"],
            has_projects=bool(resume_analysis["projects"]),
        )
    return report
