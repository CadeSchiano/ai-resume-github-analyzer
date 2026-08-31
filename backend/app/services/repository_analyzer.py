"""Deterministic repository-level analysis built from extracted features."""

from typing import Any


# Category weights are intentionally centralized so score rules are auditable.
DOCUMENTATION_WEIGHTS = {
    "has_readme": 20,
    "has_project_description": 10,
    "has_setup_instructions": 20,
    "has_usage_instructions": 20,
    "has_screenshots": 10,
    "has_architecture_information": 10,
    "has_technology_explanation": 10,
}
ENGINEERING_WEIGHTS = {
    "has_tests": 35,
    "has_ci": 25,
    "has_dependency_management": 20,
    "has_configuration": 10,
    "has_docker": 10,
}
COMPLEXITY_WEIGHTS = {
    "has_source_code": 15,
    "has_frontend": 10,
    "has_backend": 10,
    "has_database": 10,
    "has_api": 10,
    "has_authentication": 8,
    "has_deployment": 8,
    "has_external_integration": 7,
    "has_algorithm": 7,
    "has_architecture": 15,
}
PRESENTATION_WEIGHTS = {
    "has_meaningful_name": 15,
    "has_description": 30,
    "has_homepage": 20,
    "has_readme": 25,
    "has_screenshots": 10,
}
QUALITY_WEIGHTS = {
    "has_source_code": 30,
    "is_original": 10,
    "has_default_branch": 10,
    "has_description": 10,
    "has_readme": 15,
    "has_dependency_management": 15,
    "has_topics": 10,
}
GENERIC_REPOSITORY_NAMES = {"test", "testing", "new-repository", "repository", "hello-world", "untitled"}


def _score(weights: dict[str, int], signals: dict[str, bool]) -> int:
    return sum(weight for name, weight in weights.items() if signals.get(name, False))


def _meaningful_name(name: str) -> bool:
    normalized = name.strip().casefold()
    return bool(normalized) and normalized not in GENERIC_REPOSITORY_NAMES


def _documentation_score(features: dict[str, Any]) -> int | None:
    if features.get("evidence_status", {}).get("readme", "unavailable") == "unavailable":
        return None
    signals = {"has_readme": features["has_readme"], **features["documentation"]}
    return _score(DOCUMENTATION_WEIGHTS, signals)


def _engineering_score(features: dict[str, Any]) -> int | None:
    if not features["evidence_available"]["file_tree"]:
        return None
    return _score(ENGINEERING_WEIGHTS, features)


def _complexity_score(features: dict[str, Any]) -> int | None:
    evidence = features["evidence_available"]
    if not evidence["readme"] and not evidence["file_tree"]:
        return None
    signals = {"has_source_code": features["has_source_code"], **features["complexity_evidence"]}
    return _score(COMPLEXITY_WEIGHTS, signals)


def _presentation_score(features: dict[str, Any]) -> int | None:
    if features.get("evidence_status", {}).get("readme", "unavailable") == "unavailable":
        return None
    signals = {
        "has_meaningful_name": _meaningful_name(features["name"]),
        "has_description": features["has_description"],
        "has_homepage": features["has_homepage"],
        "has_readme": features["has_readme"],
        "has_screenshots": features["documentation"]["has_screenshots"],
    }
    return _score(PRESENTATION_WEIGHTS, signals)


def _quality_score(features: dict[str, Any], repository: dict[str, Any]) -> int | None:
    if not features["evidence_available"]["file_tree"]:
        return None
    signals = {
        "has_source_code": features["has_source_code"],
        "is_original": not features["is_fork"],
        "has_default_branch": bool(repository.get("default_branch")),
        "has_description": features["has_description"],
        "has_readme": features["has_readme"],
        "has_dependency_management": features["has_dependency_management"],
        "has_topics": bool(repository.get("topics")),
    }
    return _score(QUALITY_WEIGHTS, signals)


def _recommendations(features: dict[str, Any]) -> tuple[list[str], list[str]]:
    strengths = []
    improvements = []
    available = features["evidence_available"]
    documentation = features["documentation"]

    if features["has_tests"]:
        strengths.append("Includes visible automated test files.")
    elif available["file_tree"]:
        improvements.append("Add a small automated test suite to provide public evidence of testing practices.")

    if features["has_ci"]:
        strengths.append("Includes a visible CI workflow.")
    elif available["file_tree"]:
        improvements.append("Add a CI workflow to run checks or tests automatically on changes.")

    if documentation["has_setup_instructions"] and documentation["has_usage_instructions"]:
        strengths.append("README includes setup and usage guidance.")
    elif available["readme"]:
        missing = []
        if not documentation["has_setup_instructions"]:
            missing.append("installation and environment setup")
        if not documentation["has_usage_instructions"]:
            missing.append("usage instructions")
        improvements.append(f"Expand the README with {' and '.join(missing)}.")

    if features["has_homepage"]:
        strengths.append("Provides a public project demo or homepage.")
    else:
        improvements.append("Add a demo or deployed-project link when one is publicly available.")

    if features["has_description"]:
        strengths.append("Uses a repository description to explain the project.")
    else:
        improvements.append("Add a concise repository description explaining the project and its purpose.")

    return strengths, improvements


def analyze_repository(
    repository: dict[str, Any], features: dict[str, Any]
) -> dict[str, Any]:
    """Return category scores and actionable feedback for one repository.

    A ``null`` score means GitHub did not provide enough evidence for that category;
    it is deliberately not converted to a zero.
    """
    strengths, improvements = _recommendations(features)
    return {
        "name": features["name"],
        "primary_language": features["primary_language"],
        "scores": {
            "repository_quality": _quality_score(features, repository),
            "documentation": _documentation_score(features),
            "engineering_practices": _engineering_score(features),
            "project_complexity": _complexity_score(features),
            "project_presentation": _presentation_score(features),
        },
        "frameworks_detected": features["frameworks_detected"],
        "project_types_detected": features["project_types_detected"],
        "strengths": strengths,
        "improvements": improvements,
        "evidence_available": features["evidence_available"],
    }
