import base64
from datetime import date
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services import github_service
from app.services.feature_service import extract_repository_features
from app.services.repository_analyzer import analyze_repository
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
