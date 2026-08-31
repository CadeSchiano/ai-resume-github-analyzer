"""Environment-backed configuration for local development and deployment."""

import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIRECTORY = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIRECTORY / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
FRONTEND_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
)
MAX_RESUME_FILE_SIZE_BYTES = 5 * 1024 * 1024
MAX_RESUME_REQUEST_SIZE_BYTES = MAX_RESUME_FILE_SIZE_BYTES + 1024 * 1024
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60
