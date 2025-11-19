"""Authentication endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    get_change_password_use_case,
    get_current_user_use_case,
    get_login_use_case,
    get_register_use_case,
)
from app.application.dto.auth_dto import (
    PasswordChangeDTO,
    RegisterDTO,
    TokenDTO,
    UserDTO,
    RefreshTokenDTO,
)
from app.application.use_cases.auth.change_password import ChangePasswordUseCase
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.logout import LogoutUseCase

# The get_current_user_from_token dependency is provided by the dependencies module
# This avoids circular imports while maintaining proper dependency injection
from app.api.dependencies import (
    get_current_user_from_token,
    get_refresh_token_use_case,
    get_logout_use_case,
)
from app.schema.response import StandardResponse, success

router = APIRouter()


@router.post("/login", response_model=StandardResponse[TokenDTO])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    """Login endpoint with standard response format"""
    from app.application.dto.auth_dto import LoginDTO

    dto = LoginDTO(username=form_data.username, password=form_data.password)
    result = await use_case.execute(dto)
    return success(result, message="Login successful")


@router.post("/token", response_model=TokenDTO, include_in_schema=False)
async def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: LoginUseCase = Depends(get_login_use_case),
):
    """OAuth2 compatible token endpoint (for Swagger UI)"""
    from app.application.dto.auth_dto import LoginDTO

    dto = LoginDTO(username=form_data.username, password=form_data.password)
    result = await use_case.execute(dto)
    return result


@router.post(
    "/register", response_model=StandardResponse[TokenDTO], status_code=status.HTTP_201_CREATED
)
async def register(
    register_dto: RegisterDTO, use_case: RegisterUseCase = Depends(get_register_use_case)
):
    """Register new user"""
    result = await use_case.execute(register_dto)
    return success(result, message="User registered successfully")


@router.get("/me", response_model=StandardResponse[UserDTO])
async def get_current_user_info(current_user: UserDTO = Depends(get_current_user_from_token)):
    """Get current user information"""
    return success(current_user, message="User retrieved successfully")


@router.post("/change-password")
async def change_password(
    change_dto: PasswordChangeDTO,
    current_user: UserDTO = Depends(get_current_user_from_token),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
):
    """Change user password"""
    result = await use_case.execute(current_user.id, change_dto)
    return success(result, message="Password changed successfully")


@router.post("/refresh", response_model=StandardResponse[TokenDTO])
async def refresh_access_token(
    refresh_token_dto: RefreshTokenDTO,
    refresh_use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    """Refresh access token using refresh token"""
    result = await refresh_use_case.execute(refresh_token_dto)
    return success(result, message="Access token refreshed successfully")


@router.post("/logout")
async def logout(
    refresh_token_dto: RefreshTokenDTO = None,  # Optional - user can provide refresh token to invalidate
    logout_use_case: LogoutUseCase = Depends(get_logout_use_case),
):
    """Logout endpoint to invalidate refresh tokens"""
    # Extract refresh token from request body if provided
    token = None
    if refresh_token_dto:
        token = refresh_token_dto.refresh_token
    await logout_use_case.execute(token)
    return success({}, message="Successfully logged out")
