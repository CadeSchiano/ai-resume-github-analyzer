from fastapi.testclient import TestClient

from app.config import RATE_LIMIT_WINDOW_SECONDS
from app.main import app
from app.security import RequestRateLimiter
from app.services import resume_service


def test_rate_limiter_blocks_requests_after_the_configured_limit_and_recovers():
    limiter = RequestRateLimiter(max_requests=2, window_seconds=10)

    assert limiter.allow("client", now=0)
    assert limiter.allow("client", now=1)
    assert not limiter.allow("client", now=2)
    assert limiter.allow("client", now=10)


def test_resume_validation_rejects_oversized_and_invalid_files(monkeypatch):
    monkeypatch.setattr(resume_service, "MAX_RESUME_FILE_SIZE_BYTES", 4)

    try:
        resume_service.validate_resume_pdf(b"%PDF-12345")
        assert False, "Expected oversized PDF validation to fail"
    except ValueError as error:
        assert str(error) == "PDF resume must be 5 MB or smaller."

    try:
        resume_service.validate_resume_pdf(b"no")
        assert False, "Expected invalid PDF validation to fail"
    except ValueError as error:
        assert str(error) == "Upload a valid PDF resume."


def test_api_applies_security_and_sensitive_response_headers():
    client = TestClient(app)
    root_response = client.get("/")
    upload_response = client.post(
        "/resume/extract",
        files={"resume": ("resume.txt", b"plain text", "text/plain")},
    )

    assert root_response.headers["x-content-type-options"] == "nosniff"
    assert root_response.headers["x-frame-options"] == "DENY"
    assert root_response.headers["referrer-policy"] == "no-referrer"
    assert upload_response.status_code == 400
    assert upload_response.headers["cache-control"] == "no-store"


def test_rate_limit_retry_header_uses_the_configured_window():
    assert RATE_LIMIT_WINDOW_SECONDS == 60
