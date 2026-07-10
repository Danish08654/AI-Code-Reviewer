from pydantic import BaseModel

class CodeReviewRequest(BaseModel):
    code: str

class PRRequest(BaseModel):
    repo: str
    pr_number: int