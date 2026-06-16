import sys
from dotenv import load_dotenv
from app.github_client import get_pr_diff
from app.parser import split_diff_by_file
from app.sqs_client import send_review_job

load_dotenv()

MAX_CHARS = 3000


def orchestrate(repo: str, pr_number: int):
    diff = get_pr_diff(repo, pr_number)
    files = split_diff_by_file(diff)

    sent_count = 0
    skipped_count = 0

    for file_name, chunk in files.items():
        if len(chunk) > MAX_CHARS:
            print(f"Skipping large file: {file_name} ({len(chunk)} chars)")
            skipped_count += 1
            continue

        send_review_job(repo, pr_number, file_name, chunk)
        print(f"Queued review job for {file_name}")
        sent_count += 1

    print(f"\nQueued {sent_count} jobs. Skipped {skipped_count} files.")

def lambda_handler(event, context):
    repo = event["repo"]
    pr_number = int(event["pr_number"])

    orchestrate(repo, pr_number)

    return {
        "statusCode": 200,
        "body": f"Queued review jobs for {repo} PR #{pr_number}"
    }


def main():
    repo = sys.argv[sys.argv.index("--repo") + 1]
    pr = int(sys.argv[sys.argv.index("--pr") + 1])
    orchestrate(repo, pr)


if __name__ == "__main__":
    main()