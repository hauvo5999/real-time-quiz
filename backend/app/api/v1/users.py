from fastapi import APIRouter, HTTPException, status
from app.models.user import User
from typing import List

from app.schemas.user import UserBase

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": "User not found"},
        400: {"description": "Bad request"},
    },
)

@router.post("/", 
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user with the following information:",
    response_description="The created user"
)
async def create_user(user: UserBase):
    """
    Create a new user with the following information:

    - **username**: unique username
    - **email**: valid email address
    - **password_hash**: hashed password
    """
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return await UserBase.from_tortoise_orm(user_obj)

@router.get("/", 
    response_model=List[UserBase],
    summary="Get all users",
    description="Retrieve a list of all users in the system"
)
async def get_users():
    """
    Retrieve all users.
    
    Returns a list of all users in the system.
    """
    return await UserBase.from_queryset(User.all())

@router.get("/{user_id}", 
    response_model=UserBase,
    summary="Get a specific user",
    description="Retrieve a specific user by their ID",
    responses={
        404: {"description": "User not found"},
    }
)
async def get_user(user_id: int):
    """
    Retrieve a specific user by their ID.

    - **user_id**: The ID of the user to retrieve
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return await UserBase.from_tortoise_orm(user) 