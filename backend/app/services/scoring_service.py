"""Deterministic scoring for GitHub developer-readiness evidence."""

from typing import Any


CATEGORY_WEIGHTS = {
    "repository_quality": 20,
    "documentation": 15,
    "engineering_practices": 20,
    "project_complexity": 20,
    "technical_breadth": 10,
    "project_presentation": 10,
    "activity": 5,
}
MIN_MEANINGFUL_LANGUAGE_SHARE = 0.10
LANGUAGE_FAMILIES = {
    "JavaScript": "JavaScript/TypeScript",
    "TypeScript": "JavaScript/TypeScript",
    "Python": "Python",
    "Java": "JVM",
    "Kotlin": "JVM",
    "Scala": "JVM",
    "C": "C/C++",
    "C++": "C/C++",
    "C#": "C#/.NET",
    "Go": "Go",
    "Rust": "Rust",
    "Ruby": "Ruby",
    "PHP": "PHP",
    "Swift": "Swift",
}


def calculate_score(
    repo_count: int,
    total_stars: int,
    readme_count: int,
    language_count: int = 0,
):
    """Legacy score retained temporarily for the existing /github route.

    New developer-readiness reports must use ``calculate_github_scores``.
    """
    score = 0

    # Repository Count (30 pts)
    score += min(repo_count * 3, 30)

    # Stars (20 pts)
    score += min(total_stars, 20)

    # README Coverage (30 pts)
    score += min(readme_count * 4, 30)

    # Language Diversity (20 pts)
    score += min(language_count * 5, 20)

    return min(score, 100)


def _average(scores: list[int | None]) -> int | None:
    available_scores = [score for score in scores if score is not None]
    if not available_scores:
        return None
    return round(sum(available_scores) / len(available_scores))


def _meaningful_records(
    repository_analyses: list[dict[str, Any]], repository_features: list[dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Use original repositories with visible source code as project evidence."""
    analyses_by_name = {analysis["name"]: analysis for analysis in repository_analyses}
    return [
        (analyses_by_name[features["name"]], features)
        for features in repository_features
        if features["name"] in analyses_by_name
        and not features["is_fork"]
        and features["has_source_code"]
    ]


def _technical_breadth_score(records: list[tuple[dict[str, Any], dict[str, Any]]]) -> int:
    """Reward meaningful variety, with caps so language count cannot dominate."""
    language_families = set()
    frameworks = set()
    project_types = set()

    for analysis, features in records:
        languages = features["languages"]
        total_bytes = sum(languages.values())
        primary_language = features.get("primary_language")

        for language, byte_count in languages.items():
            is_material = total_bytes > 0 and byte_count / total_bytes >= MIN_MEANINGFUL_LANGUAGE_SHARE
            if is_material or language == primary_language:
                language_families.add(LANGUAGE_FAMILIES.get(language, language))

        frameworks.update(analysis["frameworks_detected"])
        project_types.update(analysis["project_types_detected"])

    language_score = (0, 40, 65, 75)[min(len(language_families), 3)]
    framework_score = min(len(frameworks) * 5, 15)
    project_type_score = min(len(project_types) * 5, 10)
    return language_score + framework_score + project_type_score


def _score_from_records(
    records: list[tuple[dict[str, Any], dict[str, Any]]], category: str
) -> int | None:
    return _average([analysis["scores"][category] for analysis, _ in records])


def calculate_github_scores(
    repository_analyses: list[dict[str, Any]], repository_features: list[dict[str, Any]]
) -> dict[str, Any]:
    """Calculate weighted GitHub category scores from repository evidence.

    An empty, successfully collected profile scores zero. If repositories exist but
    their required GitHub evidence was unavailable, affected categories are null
    and no overall score is returned.
    """
    records = _meaningful_records(repository_analyses, repository_features)
    all_tree_data_available = all(
        feature["evidence_available"]["file_tree"] for feature in repository_features
    )

    if not records:
        unavailable = bool(repository_features) and not all_tree_data_available
        categories = {
            category: None if unavailable else 0 for category in CATEGORY_WEIGHTS
        }
    else:
        categories = {
            "repository_quality": _score_from_records(records, "repository_quality"),
            "documentation": _score_from_records(records, "documentation"),
            "engineering_practices": _score_from_records(records, "engineering_practices"),
            "project_complexity": _score_from_records(records, "project_complexity"),
            "technical_breadth": _technical_breadth_score(records),
            "project_presentation": _score_from_records(records, "project_presentation"),
            "activity": round(
                100
                * sum(features["has_recent_activity"] for _, features in records)
                / len(records)
            ),
        }

    if any(score is None for score in categories.values()):
        github_score = None
    else:
        github_score = round(
            sum(categories[category] * weight for category, weight in CATEGORY_WEIGHTS.items())
            / 100
        )

    return {"github_score": github_score, "categories": categories}
