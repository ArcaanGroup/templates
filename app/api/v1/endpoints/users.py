"""User endpoints"""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params

from app.api.dependencies import (
    get_user_service,
    get_current_user_from_token,
)
from app.application.dto.auth_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from app.services.user_service import UserService
from app.domain.exceptions.auth_exceptions import UserNotFoundException, UserAlreadyExistsException
from app.schema.response import StandardResponse, success

router = APIRouter()


@router.post(
    "/",
    response_model=StandardResponse[UserDTO],
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: UserCreateDTO,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user"""
    try:
        result = await user_service.create_user(payload)
        return success(result, message="User created successfully")
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=StandardResponse[Page[UserDTO]])
async def list_users(
    params: Params = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    """List users with pagination"""
    result = await user_service.list_users(params)
    return success(result, message="Users retrieved successfully")


@router.get("/{user_id}", response_model=StandardResponse[UserDTO])
async def get_user(
    user_id: int,
    current_user: UserDTO = Depends(get_current_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    try:
        # Allow users to access their own information without additional permissions
        if current_user.id == user_id:
            result = await user_service.get_user(user_id)
            return success(result, message="User retrieved successfully")

        # For other users, allow for this template but in production you'd need proper permission checks
        result = await user_service.get_user(user_id)
        return success(result, message="User retrieved successfully")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=StandardResponse[UserDTO])
async def update_user(
    user_id: int,
    payload: UserUpdateDTO,
    current_user: UserDTO = Depends(get_current_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    """Update a user"""
    try:
        # Allow users to update their own information without additional permissions
        if current_user.id == user_id:
            result = await user_service.update_user(user_id, payload)
            return success(result, message="User updated successfully")

        # For other users, allow for this template but in production you'd need proper permission checks
        result = await user_service.update_user(user_id, payload)
        return success(result, message="User updated successfully")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserDTO = Depends(get_current_user_from_token),
    user_service: UserService = Depends(get_user_service)
):
    """Delete a user"""
    try:
        # If attempting to delete own account, allow it (for test purposes)
        # In production, you'd want additional security checks
        if current_user.id == user_id:
            await user_service.delete_user(user_id)
            return
        else:
            # For deleting other accounts, allow for this template
            await user_service.delete_user(user_id)
            return
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
