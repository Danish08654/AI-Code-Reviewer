from fastapi import APIRouter
from models.schemas import CodeReviewRequest
from services.review_service import ReviewService

router = APIRouter()

review_service = ReviewService()


@router.get("/")
def home():
    return {"message": "AI Code Reviewer Running"}


@router.post("/review")
def review_code(data: CodeReviewRequest):

    return review_service.review_code(
        data.code
    )