from collections import Counter

from fastapi import APIRouter, HTTPException

from app.services.github_service import (
    GitHubServiceError,
    get_user,
    get_repositories,
    repository_has_readme
)

from app.services.scoring_service import (
    calculate_score
)

router = APIRouter(
    prefix="/github",
    tags=["GitHub"]
)


@router.get("/{username}")
def analyze_github(username: str):
    try:
        user = get_user(username)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="GitHub user not found"
            )

        repos = get_repositories(username)
    except GitHubServiceError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


    total_stars = 0
    readme_count = 0
    languages = Counter()

    for repo in repos:

        total_stars += repo["stargazers_count"]

        if repo["language"]:
            languages[repo["language"]] += 1

        if repository_has_readme(
            username,
            repo["name"]
        ):
            readme_count += 1

    score = calculate_score(
        repo_count=len(repos),
        total_stars=total_stars,
        readme_count=readme_count
    )

    return {
        "username": username,
        "repo_count": len(repos),
        "total_stars": total_stars,
        "languages": dict(languages),
        "repos_with_readme": readme_count,
        "repos_without_readme": len(repos) - readme_count,
        "score": score
    }
