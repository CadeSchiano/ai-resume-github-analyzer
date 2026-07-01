from collections import Counter

from app.services.github_service import (
    get_user,
    get_repositories,
    repository_has_readme
)

from app.services.scoring_service import calculate_score


def generate_report(username: str):

    user = get_user(username)

    if not user:
        return None

    repos = get_repositories(username)

    total_stars = 0
    readme_count = 0
    languages = Counter()

    for repo in repos:

        total_stars += repo["stargazers_count"]

        if repo["language"]:
            languages[repo["language"]] += 1

        if repository_has_readme(username, repo["name"]):
            readme_count += 1

    score = calculate_score(
        repo_count=len(repos),
        total_stars=total_stars,
        readme_count=readme_count,
        language_count=len(languages)
    )

    strengths = []
    improvements = []

    if len(repos) >= 5:
        strengths.append("Has multiple public repositories")
    else:
        improvements.append("Create more public repositories")

    if readme_count >= len(repos) * 0.75:
        strengths.append("Most repositories include documentation")
    else:
        improvements.append("Add README files to more repositories")

    if len(languages) >= 3:
        strengths.append("Uses multiple programming languages")
    else:
        improvements.append("Explore projects in additional languages")

    if total_stars >= 10:
        strengths.append("Repositories have community engagement")
    else:
        improvements.append("Build projects that attract engagement")

    return {
        "username": username,
        "score": score,
        "repo_count": len(repos),
        "total_stars": total_stars,
        "languages": dict(languages),
        "strengths": strengths,
        "improvements": improvements
    }