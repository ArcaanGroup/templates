"""Authentication service for business logic operations"""

from typing import Optional
from datetime import datetime, timedelta
import uuid

from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.refresh_token import RefreshTokenModel
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.refresh_token_repository import SQLAlchemyRefreshTokenRepository
from app.application.dto.auth_dto import LoginDTO, RegisterDTO, TokenDTO, UserCreateDTO
from app.domain.exceptions.auth_exceptions import UserNotFoundException
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token


class AuthService:
    """Service class for authentication business logic"""

    def __init__(
        self,
        user_repository: SQLAlchemyUserRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def login(self, login_dto: LoginDTO) -> TokenDTO:
        """Authenticate user and return tokens"""
        # Get user by username or email
        user = await self.user_repository.get_by_username_or_email(login_dto.username)
        if not user or not verify_password(login_dto.password, user.hashed_password):
            raise UserNotFoundException("Invalid username or password")

        if not user.is_active:
            raise UserNotFoundException("User account is deactivated")

        # Create tokens
        access_token = create_access_token(data={"sub": user.username})
        refresh_token = create_refresh_token(data={"sub": user.username, "type": "refresh"})

        # Store refresh token in database
        refresh_token_model = RefreshTokenModel(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)  # 30 days expiry
        )
        await self.refresh_token_repository.create_with_model(refresh_token_model)

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def register(self, register_dto: RegisterDTO) -> TokenDTO:
        """Register a new user and return tokens"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_username_or_email(register_dto.username)
        if existing_user:
            raise UserNotFoundException(f"User with username '{register_dto.username}' already exists")

        existing_user = await self.user_repository.get_by_email(register_dto.email)
        if existing_user:
            raise UserNotFoundException(f"User with email '{register_dto.email}' already exists")

        # Create new user
        hashed_password = get_password_hash(register_dto.password)
        user_model = UserModel(
            username=register_dto.username,
            email=register_dto.email,
            hashed_password=hashed_password,
            is_active=True
        )
        created_user = await self.user_repository.create_with_model(user_model)

        # Create tokens
        access_token = create_access_token(data={"sub": created_user.username})
        refresh_token = create_refresh_token(data={"sub": created_user.username, "type": "refresh"})

        # Store refresh token in database
        refresh_token_model = RefreshTokenModel(
            token=refresh_token,
            user_id=created_user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)  # 30 days expiry
        )
        await self.refresh_token_repository.create_with_model(refresh_token_model)

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def get_current_user(self, token: str) -> UserModel:
        """Get current user from token"""
        from app.core.security import get_current_user as get_user_from_token
        user_data = get_user_from_token(token)

        user = await self.user_repository.get_by_username_or_email(user_data.username)
        if not user:
            raise UserNotFoundException("User not found")

        return user

    async def logout(self, refresh_token: str) -> bool:
        """Logout user by deactivating refresh token"""
        # In this implementation, we just delete the refresh token
        token_model = await self.refresh_token_repository.get_by_token(refresh_token)
        if token_model:
            await self.refresh_token_repository.delete_by_token(refresh_token)
            return True
        return False

    async def refresh_token(self, refresh_token: str) -> TokenDTO:
        """Refresh access token using refresh token"""
        from app.core.security import decode_refresh_token
        try:
            payload = decode_refresh_token(refresh_token)
            username = payload.get("sub")
            if not username:
                raise UserNotFoundException("Invalid refresh token")
        except:
            raise UserNotFoundException("Invalid refresh token")

        # Verify token exists and is active in database
        token_model = await self.refresh_token_repository.get_by_token(refresh_token)
        if not token_model or not token_model.is_active or token_model.expires_at < datetime.utcnow():
            raise UserNotFoundException("Invalid or expired refresh token")

        # Check if user still exists
        user = await self.user_repository.get_by_username_or_email(username)
        if not user or not user.is_active:
            raise UserNotFoundException("User not found or inactive")

        # Create new tokens
        new_access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username, "type": "refresh"})

        # Update refresh token in database
        await self.refresh_token_repository.delete_by_token(refresh_token)
        new_refresh_token_model = RefreshTokenModel(
            token=new_refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)  # 30 days expiry
        )
        await self.refresh_token_repository.create_with_model(new_refresh_token_model)

        return TokenDTO(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
