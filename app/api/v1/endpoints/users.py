"""User endpoints"""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params

from app.api.dependencies import (
    get_create_user_use_case,
    get_delete_user_use_case,
    get_get_user_use_case,
    get_list_users_use_case,
    get_update_user_use_case,
)
from app.application.dto.auth_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.delete_user import DeleteUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
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
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """Create a new user"""
    try:
        result = await use_case.execute(payload)
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
    use_case: ListUsersUseCase = Depends(get_list_users_use_case)
):
    """List users with pagination"""
    result = await use_case.execute(params)
    return success(result, message="Users retrieved successfully")


@router.get("/{user_id}", response_model=StandardResponse[UserDTO])
async def get_user(
    user_id: int,
    use_case: GetUserUseCase = Depends(get_get_user_use_case)
):
    """Get user by ID"""
    try:
        result = await use_case.execute(user_id)
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
    use_case: UpdateUserUseCase = Depends(get_update_user_use_case)
):
    """Update a user"""
    try:
        result = await use_case.execute(user_id, payload)
        return success(result, message="User updated successfully")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    use_case: DeleteUserUseCase = Depends(get_delete_user_use_case)
):
    """Delete a user"""
    try:
        await use_case.execute(user_id)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
