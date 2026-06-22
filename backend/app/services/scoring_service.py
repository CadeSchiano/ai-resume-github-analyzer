def calculate_score(
    repo_count: int,
    total_stars: int,
    readme_count: int
):

    score = 0

    # Repository Count
    score += min(repo_count * 3, 30)

    # Stars
    score += min(total_stars, 30)

    # Documentation
    score += min(readme_count * 4, 40)

    return min(score, 100)