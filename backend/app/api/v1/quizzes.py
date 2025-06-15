from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(
    prefix="/quizzes",
    tags=["quizzes"],
    responses={
        404: {"description": "Post not found"},
        400: {"description": "Bad request"},
    },
)
