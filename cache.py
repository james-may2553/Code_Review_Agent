import hashlib
import json
import os


CACHE_FILE = ".review_cache.json"


def make_cache_key(file_name: str, diff_chunk: str) -> str:
    mode = os.getenv("MOCK_REVIEW", "false").lower()
    content = f"{mode}:{file_name}:{diff_chunk}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def get_cached_review(file_name: str, diff_chunk: str):
    cache = load_cache()
    key = make_cache_key(file_name, diff_chunk)
    return cache.get(key)


def save_review(file_name: str, diff_chunk: str, comments: list) -> None:
    cache = load_cache()
    key = make_cache_key(file_name, diff_chunk)
    cache[key] = comments
    save_cache(cache)