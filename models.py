from pydantic import BaseModel
from typing import List

class ReviewComment(BaseModel):
    file: str
    line: int
    severity: str  # "low", "medium", "high"
    issue: str
    suggestion: str

class FileReview(BaseModel):
    comments: List[ReviewComment]