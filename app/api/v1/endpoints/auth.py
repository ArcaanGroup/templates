"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import get_login_use_case
from app.application.dto.auth_dto import TokenDTO, UserDTO
from app.application.use_cases.auth.login import LoginUseCase
from app.core.security import get_current_user
from app.schema.response import StandardResponse, success

router = APIRouter()


@router.post(
    "/login",
    response_model=StandardResponse[TokenDTO]
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUseCase = Depends(get_login_use_case)
):
    """Login endpoint"""
    from app.application.dto.auth_dto import LoginDTO
    dto = LoginDTO(username=form_data.username, password=form_data.password)
    result = await use_case.execute(dto)
    return success(result, message="Login successful")


@router.get(
    "/me",
    response_model=StandardResponse[UserDTO]
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    user_dto = UserDTO(username=current_user["username"])
    return success(user_dto, message="User retrieved successfully")


@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    """Example protected route"""
    return success(
        {"message": f"Hello {current_user['username']}, you are authenticated!"},
        message="Access granted"
    )

