"""Assemble the final deterministic GitHub analyzer report."""

from typing import Any

from app.services.feature_service import extract_repository_features
from app.services.github_service import collect_repository_evidence, get_repositories, get_user
from app.services.repository_analyzer import analyze_repository
from app.services.scoring_service import calculate_github_scores


REPOSITORY_RANK_WEIGHTS = {
    "repository_quality": 20,
    "documentation": 15,
    "engineering_practices": 20,
    "project_complexity": 20,
    "project_presentation": 10,
}


def _meaningful_pairs(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [
        (analysis, features)
        for analysis, features in pairs
        if not features["is_fork"] and features["has_source_code"]
    ]


def _repository_rank(analysis: dict[str, Any]) -> float:
    available_scores = [
        (analysis["scores"][category], weight)
        for category, weight in REPOSITORY_RANK_WEIGHTS.items()
        if analysis["scores"][category] is not None
    ]
    if not available_scores:
        return -1
    earned = sum(score * weight for score, weight in available_scores)
    return earned / sum(weight for _, weight in available_scores)


def _profile_feedback(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]]
) -> tuple[list[str], list[str]]:
    meaningful = _meaningful_pairs(pairs)
    strengths = []
    improvements = []

    if not meaningful:
        if not pairs:
            improvements.append("Publish a complete public project with visible source code to provide technical evidence on GitHub.")
        elif all(features["evidence_available"]["file_tree"] for _, features in pairs):
            improvements.append("Publish a project with visible source code to provide technical evidence on GitHub.")
        return strengths, improvements

    total = len(meaningful)
    strengths.append(f"{total} original public project{'s' if total != 1 else ''} contain visible source code.")

    tree_available = [features for _, features in meaningful if features["evidence_available"]["file_tree"]]
    readme_available = [features for _, features in meaningful if features["evidence_status"]["readme"] == "available"]
    readme_checked = [features for _, features in meaningful if features["evidence_status"]["readme"] != "unavailable"]
    tested = sum(features["has_tests"] for features in tree_available)
    ci_enabled = sum(features["has_ci"] for features in tree_available)
    documented = sum(
        features["documentation"]["has_setup_instructions"]
        and features["documentation"]["has_usage_instructions"]
        for features in readme_available
    )

    if tested:
        strengths.append(f"{tested} of {len(tree_available)} analyzable projects show visible test evidence.")
    if ci_enabled:
        strengths.append(f"{ci_enabled} of {len(tree_available)} analyzable projects include CI workflows.")
    if documented:
        strengths.append(f"{documented} of {len(readme_available)} analyzed READMEs include setup and usage guidance.")

    if tree_available and tested < len(tree_available):
        missing = len(tree_available) - tested
        improvements.append(
            f"Add a small automated test suite to {missing} project{'s' if missing != 1 else ''} without visible tests."
        )
    if tree_available and ci_enabled < len(tree_available):
        missing = len(tree_available) - ci_enabled
        improvements.append(
            f"Add CI checks to {missing} project{'s' if missing != 1 else ''} without a visible workflow."
        )
    if readme_checked:
        missing_readme = sum(features["evidence_status"]["readme"] == "not_found" for features in readme_checked)
        missing_guidance = len(readme_available) - documented
        if missing_readme:
            improvements.append(
                f"Add a README to {missing_readme} project{'s' if missing_readme != 1 else ''} with missing documentation."
            )
        if missing_guidance:
            improvements.append(
                f"Add installation, environment setup, and usage instructions to {missing_guidance} existing README{'s' if missing_guidance != 1 else ''}."
            )

    missing_descriptions = sum(not features["has_description"] for _, features in meaningful)
    if missing_descriptions:
        improvements.append(
            f"Add concise repository descriptions to {missing_descriptions} project{'s' if missing_descriptions != 1 else ''}."
        )

    return strengths, improvements


def generate_report(username: str) -> dict[str, Any] | None:
    """Generate a complete deterministic Phase 1 GitHub analysis report."""
    if not get_user(username):
        return None

    analyses_and_features = []
    for repository in get_repositories(username):
        if repository.get("fork"):
            continue
        evidence = collect_repository_evidence(username, repository)
        features = extract_repository_features(evidence)
        analysis = analyze_repository(repository, features)
        analyses_and_features.append((analysis, features))

    analyses = [analysis for analysis, _ in analyses_and_features]
    features = [features for _, features in analyses_and_features]
    profile_scores = calculate_github_scores(analyses, features)
    strengths, improvements = _profile_feedback(analyses_and_features)
    strongest_projects = sorted(
        (analysis for analysis, features in _meaningful_pairs(analyses_and_features)),
        key=_repository_rank,
        reverse=True,
    )[:3]

    return {
        "username": username,
        **profile_scores,
        "strongest_projects": strongest_projects,
        "repositories": analyses,
        "strengths": strengths,
        "improvements": improvements,
    }
