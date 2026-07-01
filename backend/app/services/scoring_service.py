def calculate_score(
    repo_count: int,
    total_stars: int,
    readme_count: int,
    language_count: int
):
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