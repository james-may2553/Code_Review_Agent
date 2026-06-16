import requests
import os

def get_pr_diff(repo: str, pr_number: int):
    """
    repo format: owner/repo
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")

    return response.text


def post_pr_comment(repo: str, pr_number: int, body: str):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.post(url, json={"body": body}, headers=headers)

    if response.status_code != 201:
        raise Exception(f"Failed to post comment: {response.status_code} {response.text}")
    
def get_pr_details(repo: str, pr_number: int):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")

    return response.json()

def post_inline_comments(repo: str, pr_number: int, comments: list):
    pr_data = get_pr_details(repo, pr_number)
    commit_id = pr_data["head"]["sha"]

    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/comments"

    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    for c in comments:
        payload = {
            "body": f"[{c['severity'].upper()}] {c['issue']}\n\nSuggestion: {c['suggestion']}",
            "commit_id": commit_id,
            "path": c["file"],
            "line": c["line"],
            "side": "RIGHT"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code not in [200, 201]:
            print(f"Failed to post inline comment: {response.text}")