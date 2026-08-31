import base64
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services import github_service
from app.services.cross_analysis_service import compare_resume_skills
from app.services.developer_report_service import generate_developer_report
from app.services.feature_service import extract_repository_features
from app.services.repository_analyzer import analyze_repository
from app.services.role_readiness_service import calculate_role_readiness, supported_roles
from app.services.scoring_service import calculate_github_scores


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


def complete_evidence():
    repository = {
        "name": "taskboard",
        "language": "TypeScript",
        "fork": False,
        "description": "A team task board",
        "homepage": "https://example.test",
        "default_branch": "main",
        "topics": ["productivity"],
        "pushed_at": "2026-08-20T12:00:00Z",
    }
    return {
        "repository": repository,
        "readme_content": """# Taskboard

A project management app built with React, FastAPI, PostgreSQL, and Docker.

## Installation
Install dependencies, then configure the server.

## Usage
Use the REST API endpoints after login with JWT authentication.

## Architecture
The frontend communicates with the backend through an external API integration.

![Screenshot](docs/screenshot.png)

## Tech stack
React and FastAPI.
""",
        "file_paths": [
            "README.md",
            "src/app.tsx",
            "tests/test_api.py",
            ".github/workflows/test.yml",
            "package.json",
            "Dockerfile",
            ".env.example",
        ],
        "collection_status": {
            "readme": "available",
            "file_tree": "available",
            "languages": "available",
        },
        "languages": {"TypeScript": 900, "Python": 100},
    }


def test_repository_pagination_and_request_failure():
    responses = iter(
        [
            FakeResponse(200, [{"name": "first"}] * 100),
            FakeResponse(200, [{"name": "last"}]),
        ]
    )
    with patch("app.services.github_service._get", side_effect=lambda *args, **kwargs: next(responses)):
        assert len(github_service.get_repositories("sample")) == 101

    with patch("app.services.github_service._get", return_value=None):
        assert github_service.get_repositories("sample") == []


def test_repository_evidence_decodes_readme_and_preserves_statuses():
    readme = base64.b64encode(b"# Demo\n\nInstall with pip.").decode()
    responses = iter(
        [
            FakeResponse(200, {"content": readme, "encoding": "base64"}),
            FakeResponse(200, {"tree": [{"path": "tests/test_app.py"}], "truncated": False}),
            FakeResponse(200, {"Python": 1234}),
        ]
    )
    repository = {"name": "demo", "default_branch": "main"}
    with patch("app.services.github_service._get", side_effect=lambda *args, **kwargs: next(responses)):
        evidence = github_service.collect_repository_evidence("sample", repository)

    assert evidence["readme_content"].startswith("# Demo")
    assert evidence["file_paths"] == ["tests/test_app.py"]
    assert evidence["languages"] == {"Python": 1234}
    assert evidence["collection_status"] == {
        "readme": "available",
        "file_tree": "available",
        "languages": "available",
    }


def test_feature_extraction_detects_documentation_and_engineering_evidence():
    features = extract_repository_features(complete_evidence(), reference_date=date(2026, 8, 27))

    assert all(
        features[key]
        for key in (
            "has_readme",
            "has_source_code",
            "has_tests",
            "has_ci",
            "has_dependency_management",
            "has_docker",
            "has_configuration",
            "has_recent_activity",
        )
    )
    assert features["frameworks_detected"] == ["FastAPI", "React"]
    assert features["project_types_detected"] == ["full_stack"]
    assert all(features["documentation"].values())


def test_missing_readme_is_scored_as_missing_not_unavailable():
    evidence = {
        "repository": {"name": "documentless", "description": "Demo", "default_branch": "main", "fork": False},
        "readme_content": None,
        "file_paths": ["src/main.py"],
        "collection_status": {"readme": "not_found", "file_tree": "available", "languages": "available"},
        "languages": {"Python": 100},
    }
    features = extract_repository_features(evidence)
    analysis = analyze_repository(evidence["repository"], features)

    assert analysis["scores"]["documentation"] == 0
    assert analysis["scores"]["project_presentation"] == 45


def test_unavailable_evidence_is_not_scored_as_zero():
    features = extract_repository_features(
        {
            "repository": {"name": "unknown"},
            "collection_status": {"readme": "unavailable", "file_tree": "unavailable", "languages": "unavailable"},
        }
    )
    analysis = analyze_repository({"name": "unknown"}, features)

    assert all(score is None for score in analysis["scores"].values())


def test_profile_scores_are_weighted_and_empty_profiles_score_zero():
    evidence = complete_evidence()
    features = extract_repository_features(evidence, reference_date=date(2026, 8, 27))
    analysis = analyze_repository(evidence["repository"], features)

    result = calculate_github_scores([analysis], [features])
    assert result["github_score"] == 97
    assert result["categories"]["technical_breadth"] == 80
    assert calculate_github_scores([], [])["github_score"] == 0


def test_analysis_api_returns_a_stable_phase_one_report():
    report = {
        "username": "sample",
        "github_score": 74,
        "categories": {"documentation": 70},
        "strongest_projects": [],
        "repositories": [],
        "strengths": [],
        "improvements": [],
    }
    client = TestClient(app)
    with patch("app.routes.analysis.generate_report", return_value=report):
        response = client.get("/analysis/sample")

    assert response.status_code == 200
    assert response.json() == report


def test_analysis_api_returns_404_for_unknown_user():
    client = TestClient(app)
    with patch("app.routes.analysis.generate_report", return_value=None):
        response = client.get("/analysis/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "GitHub user not found"


def test_cross_analysis_reports_only_public_repository_evidence():
    comparisons = compare_resume_skills(
        ["Python", "React", "Docker", "FastAPI"],
        [
            {"name": "api-service", "is_fork": False, "technologies_detected": ["Python", "Docker"]},
            {"name": "dashboard", "is_fork": False, "technologies_detected": ["Python", "React"]},
            {"name": "forked-demo", "is_fork": True, "technologies_detected": ["FastAPI"]},
        ],
    )

    assert comparisons == [
        {
            "skill": "Python",
            "evidence_level": "strong_public_evidence",
            "evidence_repositories": ["api-service", "dashboard"],
        },
        {
            "skill": "React",
            "evidence_level": "some_public_evidence",
            "evidence_repositories": ["dashboard"],
        },
        {
            "skill": "Docker",
            "evidence_level": "some_public_evidence",
            "evidence_repositories": ["api-service"],
        },
        {
            "skill": "FastAPI",
            "evidence_level": "no_public_github_evidence_found",
            "evidence_repositories": [],
        },
    ]


def test_developer_report_combines_existing_reports_and_cross_evidence():
    github_report = {
        "username": "sample",
        "repositories": [{"name": "api-service", "is_fork": False, "technologies_detected": ["Python"]}],
    }
    resume_report = {"skills": ["Python", "FastAPI"]}
    with patch("app.services.developer_report_service.generate_report", return_value=github_report), patch(
        "app.services.developer_report_service.generate_resume_report", return_value=resume_report
    ):
        report = generate_developer_report("sample", "resume text")

    assert report == {
        "username": "sample",
        "github_analysis": github_report,
        "resume_analysis": resume_report,
        "resume_github_evidence": [
            {"skill": "Python", "evidence_level": "some_public_evidence", "evidence_repositories": ["api-service"]},
            {"skill": "FastAPI", "evidence_level": "no_public_github_evidence_found", "evidence_repositories": []},
        ],
    }


def test_developer_report_adds_role_readiness_when_a_role_is_selected():
    github_report = {
        "username": "sample",
        "repositories": [{"name": "api-service", "is_fork": False, "technologies_detected": ["Python"]}],
    }
    resume_report = {"skills": ["Python"], "projects": ["API service"]}
    role_readiness = {"target_role": "Backend Developer", "role_readiness_score": 80}
    with patch("app.services.developer_report_service.generate_report", return_value=github_report), patch(
        "app.services.developer_report_service.generate_resume_report", return_value=resume_report
    ), patch("app.services.developer_report_service.calculate_role_readiness", return_value=role_readiness):
        report = generate_developer_report("sample", "resume text", "Backend Developer")

    assert report["role_readiness"] == role_readiness


def test_combined_analysis_api_returns_developer_report():
    expected_report = {"username": "sample", "github_analysis": {}, "resume_analysis": {}, "resume_github_evidence": []}
    client = TestClient(app)
    with patch("app.routes.analysis.extract_resume_text", return_value="Jane Developer"), patch(
        "app.routes.analysis.generate_developer_report", return_value=expected_report
    ):
        response = client.post(
            "/analysis/sample/resume",
            files={"resume": ("resume.pdf", b"%PDF-1.7 test", "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json() == expected_report


def test_combined_analysis_api_returns_a_clear_error_for_an_unsupported_role():
    client = TestClient(app)
    with patch("app.routes.analysis.extract_resume_text", return_value="Jane Developer"), patch(
        "app.routes.analysis.generate_developer_report", side_effect=ValueError("Unsupported target role: Designer")
    ):
        response = client.post(
            "/analysis/sample/resume",
            data={"target_role": "Designer"},
            files={"resume": ("resume.pdf", b"%PDF-1.7 test", "application/pdf")},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported target role: Designer"


def test_role_readiness_uses_resume_claims_public_evidence_and_projects():
    readiness = calculate_role_readiness(
        "Backend Developer",
        ["Python", "REST APIs", "PostgreSQL"],
        [
            {"skill": "Python", "evidence_level": "strong_public_evidence"},
            {"skill": "REST APIs", "evidence_level": "some_public_evidence"},
            {"skill": "PostgreSQL", "evidence_level": "no_public_github_evidence_found"},
        ],
        has_projects=True,
    )

    assert readiness == {
        "target_role": "Backend Developer",
        "role_readiness_score": 83,
        "categories": {
            "resume_skill_alignment": 45,
            "public_github_evidence": 18,
            "project_evidence": 20,
        },
        "requirements": [
            {"requirement": "backend language", "matched_resume_skills": ["Python"], "public_evidence": "strong_public_evidence"},
            {"requirement": "API technology", "matched_resume_skills": ["REST APIs"], "public_evidence": "some_public_evidence"},
            {"requirement": "database technology", "matched_resume_skills": ["PostgreSQL"], "public_evidence": "no_public_github_evidence_found"},
        ],
    }
    assert supported_roles() == [
        "Software Engineer Intern",
        "Software Engineer",
        "Backend Developer",
        "Frontend Developer",
        "Full-Stack Developer",
        "Mobile Developer",
        "AI/ML",
    ]
