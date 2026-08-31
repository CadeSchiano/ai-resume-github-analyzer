from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.resume_parser_service import parse_resume_text
from app.services.resume_report_service import generate_resume_report
from app.services.resume_scoring_service import calculate_resume_scores
from app.services.resume_service import extract_resume_text


class FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakeReader:
    is_encrypted = False
    pages = [FakePage("Jane Developer"), FakePage("Python and FastAPI")]


def test_extract_resume_text_joins_text_from_all_pages():
    with patch("app.services.resume_service.PdfReader", return_value=FakeReader()):
        text = extract_resume_text(b"%PDF-1.7")

    assert text == "Jane Developer\nPython and FastAPI"


def test_extract_resume_text_rejects_unreadable_or_empty_pdfs():
    with patch("app.services.resume_service.PdfReader", side_effect=Exception("invalid")):
        with pytest.raises(ValueError, match="could not be read"):
            extract_resume_text(b"not a PDF")

    class EmptyReader:
        is_encrypted = False
        pages = [FakePage(None)]

    with patch("app.services.resume_service.PdfReader", return_value=EmptyReader()):
        with pytest.raises(ValueError, match="No selectable text"):
            extract_resume_text(b"%PDF-1.7")


def test_resume_extract_api_accepts_pdf_uploads_without_persisting_files():
    client = TestClient(app)
    with patch("app.routes.resume.extract_resume_text", return_value="Jane Developer\nPython"):
        response = client.post(
            "/resume/extract",
            files={"resume": ("resume.pdf", b"%PDF-1.7 test", "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json() == {"text": "Jane Developer\nPython"}


def test_resume_extract_api_rejects_non_pdf_uploads():
    client = TestClient(app)
    response = client.post(
        "/resume/extract",
        files={"resume": ("resume.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload a valid PDF resume."


def test_resume_parser_extracts_sections_skills_experience_and_projects():
    parsed = parse_resume_text(
        """Jane Developer

TECHNICAL SKILLS
Python, FastAPI, React, PostgreSQL, Docker, GitHub

WORK EXPERIENCE
Software Engineering Intern | Acme | 2025
- Built REST APIs with FastAPI and PostgreSQL.
- Containerized services with Docker.

PROJECTS
Taskboard
- Built a React application with a Python backend.

EDUCATION
B.S. Computer Science
"""
    )

    assert parsed["sections"]["skills"] == "Python, FastAPI, React, PostgreSQL, Docker, GitHub"
    assert parsed["skills"] == ["Python", "React", "FastAPI", "PostgreSQL", "Docker", "GitHub", "REST APIs"]
    assert parsed["experience"] == [
        "Software Engineering Intern | Acme | 2025\n"
        "Built REST APIs with FastAPI and PostgreSQL.\n"
        "Containerized services with Docker."
    ]
    assert parsed["projects"] == [
        "Taskboard\nBuilt a React application with a Python backend."
    ]


def test_resume_parser_does_not_infer_missing_sections_or_skills():
    parsed = parse_resume_text("Taylor Developer\n\nSummary\nEntry-level developer.")

    assert parsed["sections"] == {"summary": "Entry-level developer."}
    assert parsed["skills"] == []
    assert parsed["experience"] == []
    assert parsed["projects"] == []


def test_resume_scores_are_deterministic_and_evidence_based():
    parsed = {
        "sections": {
            "skills": "Python, FastAPI, React, PostgreSQL, Docker",
            "experience": "Software Engineering Intern",
            "projects": "Taskboard",
            "education": "B.S. Computer Science",
        },
        "skills": ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
        "experience": ["Engineering Intern\nBuilt an API that reduced response time by 30%."],
        "projects": ["Taskboard\nDeveloped a React and FastAPI application used by 100 users."],
    }

    result = calculate_resume_scores(parsed)

    assert result == {
        "resume_score": 93,
        "categories": {
            "technical_skills": 30,
            "experience": 25,
            "projects": 30,
            "structure": 8,
        },
    }


def test_resume_scores_do_not_infer_evidence_that_is_absent():
    result = calculate_resume_scores({"sections": {}, "skills": [], "experience": [], "projects": []})

    assert result == {
        "resume_score": 0,
        "categories": {"technical_skills": 0, "experience": 0, "projects": 0, "structure": 0},
    }


def test_resume_report_returns_scores_evidence_and_actionable_feedback():
    report = generate_resume_report(
        """Technical Skills
Python, FastAPI, PostgreSQL

Experience
Engineering Intern
- Built a REST API that reduced response time by 30%.

Projects
Taskboard
- Developed a Python application used by 100 users.

Education
B.S. Computer Science
"""
    )

    assert report["resume_score"] == 93
    assert report["skills"] == ["Python", "FastAPI", "PostgreSQL", "REST APIs"]
    assert report["experience"] == ["Engineering Intern\nBuilt a REST API that reduced response time by 30%."]
    assert report["projects"] == ["Taskboard\nDeveloped a Python application used by 100 users."]
    assert len(report["strengths"]) == 4
    assert report["improvements"] == []


def test_resume_analyze_api_returns_the_complete_report():
    expected_report = {
        "resume_score": 74,
        "categories": {"technical_skills": 30},
        "skills": ["Python"],
        "experience": [],
        "projects": [],
        "strengths": [],
        "improvements": [],
    }
    client = TestClient(app)
    with patch("app.routes.resume.extract_resume_text", return_value="Jane Developer\nPython"), patch(
        "app.routes.resume.generate_resume_report", return_value=expected_report
    ):
        response = client.post(
            "/resume/analyze",
            files={"resume": ("resume.pdf", b"%PDF-1.7 test", "application/pdf")},
        )

    assert response.status_code == 200
    assert response.json() == expected_report
