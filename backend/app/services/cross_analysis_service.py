"""Compare explicit resume skills with public GitHub repository evidence."""

from collections import defaultdict
from typing import Any


STRONG_EVIDENCE_REPOSITORIES = 2


def compare_resume_skills(
    resume_skills: list[str], repositories: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Classify each resume skill by visible evidence across original repositories.

    This reports only what was publicly detected in the analyzed repositories. A
    missing match never means the candidate lacks the skill.
    """
    evidence_by_skill: dict[str, set[str]] = defaultdict(set)
    for repository in repositories:
        if repository.get("is_fork"):
            continue
        for technology in repository.get("technologies_detected", []):
            evidence_by_skill[technology.casefold()].add(repository["name"])

    comparisons = []
    for skill in resume_skills:
        repositories_with_evidence = sorted(evidence_by_skill[skill.casefold()])
        evidence_count = len(repositories_with_evidence)
        if evidence_count >= STRONG_EVIDENCE_REPOSITORIES:
            evidence_level = "strong_public_evidence"
        elif evidence_count:
            evidence_level = "some_public_evidence"
        else:
            evidence_level = "no_public_github_evidence_found"

        comparisons.append(
            {
                "skill": skill,
                "evidence_level": evidence_level,
                "evidence_repositories": repositories_with_evidence,
            }
        )

    return comparisons
