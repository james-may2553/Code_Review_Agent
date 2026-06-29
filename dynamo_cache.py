import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("Code-Review-Cache")


def get_cached_review(key: str):
    response = table.get_item(Key={"cache-key": key})
    comments = response.get("Item", {}).get("comments")
    return convert_decimals(comments)


def save_review(key: str, comments: list):
    table.put_item(
        Item={
            "cache-key": key,
            "comments": comments
        }
    )

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(x) for x in obj]
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return int(obj)
    return obj