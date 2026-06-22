import requests

BASE_URL = "https://api.github.com"


def get_user(username: str):
    response = requests.get(
        f"{BASE_URL}/users/{username}"
    )

    if response.status_code != 200:
        return None

    return response.json()


def get_repositories(username: str):
    response = requests.get(
        f"{BASE_URL}/users/{username}/repos?per_page=100"
    )

    if response.status_code != 200:
        return []

    return response.json()


def repository_has_readme(username: str, repo_name: str):
    response = requests.get(
        f"{BASE_URL}/repos/{username}/{repo_name}/readme"
    )

    return response.status_code == 200