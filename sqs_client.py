import boto3
import json
import os
from dotenv import load_dotenv


load_dotenv()

sqs = boto3.client("sqs", region_name="us-east-1")

QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def send_review_job(repo: str, pr_number: int, file_name: str, diff_chunk: str):
    if not QUEUE_URL:
        raise ValueError("SQS_QUEUE_URL is not set")

    message = {
        "repo": repo,
        "pr_number": pr_number,
        "file_name": file_name,
        "diff_chunk": diff_chunk,
    }

    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(message),
    )

    return response