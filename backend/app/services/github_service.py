"""GitHub API data collection for the deterministic analyzer.

This module deliberately returns raw API data and collected repository evidence.
Scoring and feature interpretation belong in later services.
"""

import base64
from typing import Any
from urllib.parse import quote

import requests

from app.config import GITHUB_TOKEN


BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT_SECONDS = 10
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def _headers() -> dict[str, str]:
    headers = DEFAULT_HEADERS.copy()
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def _get(path: str, params: dict[str, Any] | None = None) -> requests.Response | None:
    """Make one GitHub request and convert network failures into missing data."""
    try:
        return requests.get(
            f"{BASE_URL}{path}",
            params=params,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        return None


def get_user(username: str) -> dict[str, Any] | None:
    response = _get(f"/users/{quote(username, safe='')}")

    if response is None or response.status_code != 200:
        return None

    return response.json()


def get_repositories(username: str) -> list[dict[str, Any]]:
    """Return every public repository available through GitHub pagination."""
    repositories = []
    page = 1

    while True:
        response = _get(
            f"/users/{quote(username, safe='')}/repos",
            params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
        )

        if response is None or response.status_code != 200:
            return []

        batch = response.json()
        if not batch:
            return repositories

        repositories.extend(batch)

        if len(batch) < 100:
            return repositories

        page += 1


def get_repository_readme(username: str, repo_name: str) -> tuple[str | None, str]:
    """Return decoded README content and its retrieval status.

    A missing README is distinct from an API failure so later analysis never treats
    unavailable GitHub data as evidence that documentation is absent.
    """
    response = _get(
        f"/repos/{quote(username, safe='')}/{quote(repo_name, safe='')}/readme"
    )

    if response is None:
        return None, "unavailable"
    if response.status_code == 404:
        return None, "not_found"
    if response.status_code != 200:
        return None, "unavailable"

    payload = response.json()
    content = payload.get("content")
    if not content or payload.get("encoding") != "base64":
        return None, "available"

    try:
        return base64.b64decode(content).decode("utf-8", errors="replace"), "available"
    except (ValueError, UnicodeDecodeError):
        return None, "available"


def repository_has_readme(username: str, repo_name: str) -> bool:
    """Compatibility helper for existing callers."""
    _, status = get_repository_readme(username, repo_name)
    return status == "available"


def get_repository_file_tree(
    username: str, repo_name: str, default_branch: str | None
) -> tuple[list[str], bool, str]:
    """Return paths from GitHub's recursive tree API without cloning the repo."""
    if not default_branch:
        return [], False, "unavailable"

    response = _get(
        "/repos/"
        f"{quote(username, safe='')}/{quote(repo_name, safe='')}"
        f"/git/trees/{quote(default_branch, safe='')}",
        params={"recursive": "1"},
    )

    if response is None:
        return [], False, "unavailable"
    if response.status_code == 409:
        return [], False, "empty"
    if response.status_code != 200:
        return [], False, "unavailable"

    payload = response.json()
    paths = [entry["path"] for entry in payload.get("tree", []) if "path" in entry]
    return paths, bool(payload.get("truncated")), "available"


def get_repository_languages(username: str, repo_name: str) -> tuple[dict[str, int], str]:
    """Return GitHub's byte-count language breakdown for one repository."""
    response = _get(
        f"/repos/{quote(username, safe='')}/{quote(repo_name, safe='')}/languages"
    )

    if response is None or response.status_code != 200:
        return {}, "unavailable"

    return response.json(), "available"


def collect_repository_evidence(
    username: str, repository: dict[str, Any]
) -> dict[str, Any]:
    """Collect the API evidence needed for later per-repository analysis.

    The returned structure intentionally contains evidence only; it does not
    decide whether a repository has tests, CI, or a particular framework.
    """
    repo_name = repository["name"]
    readme_content, readme_status = get_repository_readme(username, repo_name)
    file_paths, tree_truncated, tree_status = get_repository_file_tree(
        username, repo_name, repository.get("default_branch")
    )
    languages, languages_status = get_repository_languages(username, repo_name)

    return {
        "repository": repository,
        "readme_content": readme_content,
        "file_paths": file_paths,
        "file_tree_truncated": tree_truncated,
        "collection_status": {
            "readme": readme_status,
            "file_tree": tree_status,
            "languages": languages_status,
        },
        "languages": languages,
    }
