"""Convert collected GitHub evidence into deterministic repository features."""

from datetime import date, datetime, timedelta
import re
from typing import Any

from app.services.resume_parser_service import SKILL_PATTERNS


RECENT_ACTIVITY_DAYS = 365

DEPENDENCY_FILES = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "poetry.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "cargo.toml",
    "go.mod",
}
SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs",
    ".cs", ".cpp", ".c", ".h", ".rb", ".php", ".swift", ".scala",
}
FRAMEWORK_PATTERNS = {
    "React": r"\breact\b",
    "Next.js": r"\bnext(?:\.js)?\b",
    "Vue": r"\bvue(?:\.js)?\b",
    "Angular": r"\bangular\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "FastAPI": r"\bfastapi\b",
    "Spring": r"\bspring(?: boot)?\b",
    "Express": r"\bexpress(?:\.js)?\b",
    "Laravel": r"\blaravel\b",
    "Ruby on Rails": r"\bruby on rails\b|\brails\b",
}


def _paths(evidence: dict[str, Any]) -> list[str]:
    normalized_paths = []
    for path in evidence.get("file_paths", []):
        normalized = path.casefold()
        if normalized.startswith("./"):
            normalized = normalized[2:]
        normalized_paths.append(normalized)
    return normalized_paths


def _has_path(paths: list[str], filename: str) -> bool:
    return any(path == filename or path.endswith(f"/{filename}") for path in paths)


def _has_prefix(paths: list[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in paths)


def _readme_features(readme: str | None, readme_available: bool) -> dict[str, bool]:
    text = (readme or "").casefold()
    return {
        "has_project_description": readme_available and len(text.strip()) >= 80,
        "has_setup_instructions": bool(re.search(r"\b(install|installation|setup|getting started)\b", text)),
        "has_usage_instructions": bool(re.search(r"\b(usage|how to use|examples?)\b", text)),
        "has_screenshots": bool(re.search(r"!\[[^]]*\]\([^)]*\)|<img\b", text)),
        "has_architecture_information": bool(re.search(r"\b(architecture|system design)\b", text)),
        "has_technology_explanation": bool(re.search(r"\b(tech stack|technologies|built with)\b", text)),
    }


def _recent_activity(pushed_at: str | None, reference_date: date) -> bool:
    if not pushed_at:
        return False
    try:
        pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).date()
    except ValueError:
        return False
    return pushed_date >= reference_date - timedelta(days=RECENT_ACTIVITY_DAYS)


def extract_repository_features(
    evidence: dict[str, Any], reference_date: date | None = None
) -> dict[str, Any]:
    """Extract public-evidence signals without assigning any scores.

    When a GitHub API resource could not be collected, the matching availability
    field is false. Downstream scoring must not interpret that as missing evidence.
    """
    repository = evidence.get("repository", {})
    status = evidence.get("collection_status", {})
    tree_available = status.get("file_tree") == "available"
    readme_available = status.get("readme") == "available"
    languages_available = status.get("languages") == "available"
    paths = _paths(evidence)
    readme = evidence.get("readme_content")
    documentation = _readme_features(readme, readme_available)

    has_tests = tree_available and any(
        path.startswith(("tests/", "test/"))
        or "/tests/" in path
        or "/test/" in path
        or path.rsplit("/", 1)[-1].startswith("test_")
        or path.rsplit("/", 1)[-1].endswith("_test.py")
        for path in paths
    )
    has_ci = tree_available and _has_prefix(paths, ".github/workflows/")
    has_docker = tree_available and any(
        _has_path(paths, filename) for filename in ("dockerfile", "docker-compose.yml", "docker-compose.yaml")
    )
    has_dependencies = tree_available and any(
        _has_path(paths, filename) for filename in DEPENDENCY_FILES
    )
    has_configuration = tree_available and any(
        _has_path(paths, filename) for filename in (".env.example", "config.example", "settings.example")
    )
    languages = evidence.get("languages", {}) if languages_available else {}
    has_source_code = tree_available and (
        bool(languages) or any(path.endswith(extension) for path in paths for extension in SOURCE_EXTENSIONS)
    )
    readme_text = (readme or "").casefold()
    frameworks = sorted(
        framework for framework, pattern in FRAMEWORK_PATTERNS.items() if re.search(pattern, readme_text)
    )
    has_frontend = bool(frameworks and any(name in frameworks for name in ("React", "Next.js", "Vue", "Angular"))) or _has_path(paths, "index.html")
    has_backend = bool(frameworks and any(name in frameworks for name in ("Django", "Flask", "FastAPI", "Spring", "Express", "Laravel", "Ruby on Rails"))) or bool(
        re.search(r"\b(backend|server-side|server application)\b", readme_text)
    )
    has_database_evidence = bool(re.search(r"\b(postgresql|mysql|mongodb|sqlite|redis|supabase|firebase)\b", readme_text))
    has_api_evidence = bool(re.search(r"\b(rest|graphql|api endpoints?|openapi)\b", readme_text)) or _has_prefix(paths, "api/")
    has_authentication_evidence = bool(re.search(r"\b(authentication|authorization|oauth|login|jwt)\b", readme_text))
    has_external_integration_evidence = bool(re.search(r"\b(webhook|stripe|twilio|integration|third-party api)\b", readme_text))
    has_algorithm_evidence = bool(re.search(r"\b(algorithm|machine learning|neural network|data structure)\b", readme_text))
    technologies = set(languages)
    technologies.update(
        skill for skill, pattern in SKILL_PATTERNS.items() if re.search(pattern, readme_text)
    )
    technologies.update(frameworks)
    if has_docker:
        technologies.add("Docker")

    if has_frontend and has_backend:
        project_types = ["full_stack"]
    elif has_frontend:
        project_types = ["frontend"]
    elif has_backend:
        project_types = ["backend"]
    else:
        project_types = []

    reference_date = reference_date or date.today()
    return {
        "name": repository.get("name", ""),
        "primary_language": repository.get("language"),
        "languages": languages,
        "is_fork": bool(repository.get("fork")),
        "has_description": bool((repository.get("description") or "").strip()),
        "has_homepage": bool((repository.get("homepage") or "").strip()),
        "has_readme": readme_available,
        "has_source_code": has_source_code,
        "has_tests": has_tests,
        "has_ci": has_ci,
        "has_dependency_management": has_dependencies,
        "has_docker": has_docker,
        "has_configuration": has_configuration,
        "has_recent_activity": _recent_activity(repository.get("pushed_at"), reference_date),
        "documentation": documentation,
        "complexity_evidence": {
            "has_frontend": has_frontend,
            "has_backend": has_backend,
            "has_database": has_database_evidence,
            "has_api": has_api_evidence,
            "has_authentication": has_authentication_evidence,
            "has_deployment": has_docker or bool((repository.get("homepage") or "").strip()),
            "has_external_integration": has_external_integration_evidence,
            "has_algorithm": has_algorithm_evidence,
            "has_architecture": documentation["has_architecture_information"],
        },
        "frameworks_detected": frameworks,
        "technologies_detected": sorted(technologies),
        "project_types_detected": project_types,
        "evidence_available": {
            "readme": readme_available,
            "file_tree": tree_available,
            "languages": languages_available,
        },
        "evidence_status": {
            "readme": status.get("readme", "unavailable"),
            "file_tree": status.get("file_tree", "unavailable"),
            "languages": status.get("languages", "unavailable"),
        },
    }
