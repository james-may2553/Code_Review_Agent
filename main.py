import sys
from app.parser import split_diff_by_file
from app.reviewer import review_file
from app.github_client import get_pr_diff, post_inline_comments
from app.cache import make_cache_key
from app.dynamo_cache import get_cached_review, save_review


MAX_CHARS = 3000


def format_comment(comments):
    output = "## 🤖 AI Code Review\n\n"

    if not comments:
        return output + "No review comments found."

    for c in comments:
        output += f"**{c['file']}:{c['line']}**\n"
        output += f"- Severity: {c['severity']}\n"
        output += f"- Issue: {c['issue']}\n"
        output += f"- Suggestion: {c['suggestion']}\n\n"

    return output


def main():
    is_github_pr = "--repo" in sys.argv

    if is_github_pr:
        repo = sys.argv[sys.argv.index("--repo") + 1]
        pr = int(sys.argv[sys.argv.index("--pr") + 1])
        diff = get_pr_diff(repo, pr)
    else:
        path = sys.argv[1]
        with open(path, "r") as f:
            diff = f.read()

    files = split_diff_by_file(diff)
    all_comments = []

    for file, chunk in files.items():
        if len(chunk) > MAX_CHARS:
            print(f"Skipping large file: {file} ({len(chunk)} chars)")
            continue

        key = make_cache_key(file, chunk)
        cached_comments = get_cached_review(key)

        if cached_comments is not None:
            print(f"Using cached review for {file}")
            comments = cached_comments
        else:
            comments = review_file(file, chunk)
            save_review(key, comments)

        all_comments.extend(comments)

    for c in all_comments:
        print(f"\n[{c['severity'].upper()}] {c['file']}:{c['line']}")
        print(f"Issue: {c['issue']}")
        print(f"Suggestion: {c['suggestion']}")

    if is_github_pr:
        post_inline_comments(repo, pr, all_comments)
        print("\nPosted inline comments to GitHub PR.")


if __name__ == "__main__":
    main()