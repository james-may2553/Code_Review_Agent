import json
import boto3
import os
from dotenv import load_dotenv
from app.github_client import post_inline_comments

from app.cache import make_cache_key
from app.dynamo_cache import get_cached_review, save_review
from app.reviewer import review_file

load_dotenv()

sqs = boto3.client("sqs", region_name="us-east-1")
QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def process_job(job: dict):
    repo = job["repo"]
    pr_number = job["pr_number"]
    file_name = job["file_name"]
    diff_chunk = job["diff_chunk"]

    key = make_cache_key(file_name, diff_chunk)
    cached_comments = get_cached_review(key)

    if cached_comments is not None:
        print(f"Using cached review for {file_name}")
        comments = cached_comments
    else:
        print(f"Reviewing {file_name}")
        comments = review_file(file_name, diff_chunk)
        save_review(key, comments)

    print(f"Processed {file_name}: {len(comments)} comments")


    post_inline_comments(repo, pr_number, comments)

    print(f"Posted comments for {file_name}")

    return {
        "repo": repo,
        "pr_number": pr_number,
        "file_name": file_name,
        "comments": comments,
    }


def poll_once():
    if not QUEUE_URL:
        raise ValueError("SQS_QUEUE_URL is not set")

    response = sqs.receive_message(
        QueueUrl=QUEUE_URL,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5,
    )

    messages = response.get("Messages", [])

    if not messages:
        print("No messages found.")
        return

    message = messages[0]
    receipt_handle = message["ReceiptHandle"]
    job = json.loads(message["Body"])

    result = process_job(job)
    print(json.dumps(result, indent=2))

    sqs.delete_message(
        QueueUrl=QUEUE_URL,
        ReceiptHandle=receipt_handle,
    )

    print("Deleted message from queue.")

def lambda_handler(event, context):
    for record in event["Records"]:
        job = json.loads(record["body"])
        process_job(job)

    return {
        "statusCode": 200,
        "body": "Processed SQS messages"
    }


if __name__ == "__main__":
    poll_once()