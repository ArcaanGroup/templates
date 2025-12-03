"""User service for business logic operations"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.auth_dto import UserCreateDTO, UserDTO, UserUpdateDTO
from app.core.security import get_password_hash
from app.domain.exceptions.auth_exceptions import UserAlreadyExistsException, UserNotFoundException
from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


class UserService:
    """Service class for user business logic"""

    def __init__(
        self,
        user_repository: SQLAlchemyUserRepository,
        role_repository: SQLAlchemyRoleRepository,
        refresh_token_repository: SQLAlchemyRefreshTokenRepository,
    ):
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.refresh_token_repository = refresh_token_repository

    async def create_user(self, dto: UserCreateDTO) -> UserDTO:
        """Create a new user with validation and business logic"""
        # Check if user already exists by username
        existing_user_by_username = await self.user_repository.get_by_username(dto.username)
        if existing_user_by_username:
            raise UserAlreadyExistsException(f"User with username '{dto.username}' already exists")

        # Also check with email
        existing_user_by_email = await self.user_repository.get_by_email(dto.email)
        if existing_user_by_email:
            raise UserAlreadyExistsException(f"User with email '{dto.email}' already exists")

        # Hash the password
        hashed_password = get_password_hash(dto.password)

        # Create database model
        user_model = UserModel(
            username=dto.username,
            email=dto.email,
            hashed_password=hashed_password,
            is_active=dto.is_active,
        )

        # Add to database
        created_user = await self.user_repository.create_with_model(user_model)

        # Assign roles if specified
        if dto.role_ids:
            await self._assign_roles_to_user(created_user, dto.role_ids)
        else:
            # Assign default role if no roles were specified
            await self._assign_default_role(created_user)

        # Refresh the user to get role information
        updated_user = await self.user_repository.get_by_id(created_user.id)

        # Convert to DTO
        role_titles = [
            role.title.value if hasattr(role.title, "value") else role.title
            for role in updated_user.roles
        ]
        return UserDTO(
            id=updated_user.id,
            username=updated_user.username.value
            if hasattr(updated_user.username, "value")
            else updated_user.username,
            email=updated_user.email.value
            if hasattr(updated_user.email, "value")
            else updated_user.email,
            is_active=updated_user.is_active,
            roles=role_titles,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
        )

    async def get_user(self, user_id: int) -> UserDTO:
        """Get user by ID"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        role_titles = [
            role.title.value if hasattr(role.title, "value") else role.title for role in user.roles
        ]
        return UserDTO(
            id=user.id,
            username=user.username.value if hasattr(user.username, "value") else user.username,
            email=user.email.value if hasattr(user.email, "value") else user.email,
            is_active=user.is_active,
            roles=role_titles,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def list_users(self, params: Params) -> Page[UserDTO]:
        """List users with pagination"""
        from fastapi_pagination.ext.sqlalchemy import paginate
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.infrastructure.database.models.user import UserModel

        # Make a direct query with proper relationship loading
        query = select(UserModel).options(selectinload(UserModel.roles))
        paginated_result = await paginate(self.user_repository.session, query, params)

        result = []
        for user in paginated_result.items:  # Access the items from the paginated result
            # UserModel case - user is a UserModel from the database
            username_val = getattr(user, "username", "")
            email_val = getattr(user, "email", "")
            # For UserModel, roles are RoleModel objects which have a title attribute
            role_titles = [role.title for role in user.roles] if user.roles else []

            result.append(
                UserDTO(
                    id=getattr(user, "id", None),
                    username=username_val,
                    email=email_val,
                    is_active=getattr(user, "is_active", None),
                    roles=role_titles,
                    created_at=getattr(user, "created_at", None),
                    updated_at=getattr(user, "updated_at", None),
                )
            )

        # Return Page object using fastapi_pagination's create_page
        from fastapi_pagination import create_page

        return create_page(result, paginated_result.total, params)

    async def update_user(self, user_id: int, dto: UserUpdateDTO) -> UserDTO:
        """Update user with validation and business logic"""
        # Get existing user
        existing_user = await self.user_repository.get_by_id(user_id)
        if not existing_user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Update fields if provided
        if dto.username is not None:
            # Check if new username is already taken
            existing_with_username = await self.user_repository.get_by_username(dto.username)
            if existing_with_username and existing_with_username.id != user_id:
                raise UserAlreadyExistsException(f"Username '{dto.username}' is already taken")

            from app.domain.value_objects.username import Username

            existing_user.update_username(Username(dto.username))

        if dto.email is not None:
            # Check if new email is already taken
            existing_with_email = await self.user_repository.get_by_email(dto.email)
            if existing_with_email and existing_with_email.id != user_id:
                raise UserAlreadyExistsException(f"Email '{dto.email}' is already taken")

            from app.domain.value_objects.email import Email

            existing_user.update_email(Email(dto.email))

        if dto.is_active is not None:
            if dto.is_active:
                existing_user.activate()
            else:
                existing_user.deactivate()

        # Update the user in database
        updated_user = await self.user_repository.update(existing_user)

        # Update roles if provided
        if dto.role_ids is not None:
            await self._assign_roles_to_user(updated_user, dto.role_ids)

        # Refresh the user to get updated role information
        refreshed_user = await self.user_repository.get_by_id(updated_user.id)

        # Convert to DTO
        role_titles = [
            role.title.value if hasattr(role.title, "value") else role.title
            for role in refreshed_user.roles
        ]
        return UserDTO(
            id=refreshed_user.id,
            username=refreshed_user.username.value
            if hasattr(refreshed_user.username, "value")
            else refreshed_user.username,
            email=refreshed_user.email.value
            if hasattr(refreshed_user.email, "value")
            else refreshed_user.email,
            is_active=refreshed_user.is_active,
            roles=role_titles,
            created_at=refreshed_user.created_at,
            updated_at=refreshed_user.updated_at,
        )

    async def delete_user(self, user_id: int) -> None:
        """Delete user with business logic"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Delete refresh tokens associated with user first to avoid foreign key constraints
        await self.refresh_token_repository.delete_by_user_id(user_id)

        # Delete user
        await self.user_repository.delete(user)

    async def _assign_roles_to_user(self, user: UserModel, role_ids: List[uuid.UUID]) -> None:
        """Assign roles to a user"""
        assigned_roles = []
        for role_id in role_ids:
            role = await self.role_repository.get_by_id(str(role_id))
            if role:
                assigned_roles.append(role)

        # Update user roles
        user.roles = assigned_roles
        await self.user_repository.session.commit()
        await self.user_repository.session.refresh(user)

    async def _assign_default_role(self, user: UserModel) -> None:
        """Assign default role to user if no specific roles are assigned"""
        # Try to find a 'user' role as the default
        default_role = await self.role_repository.get_by_title("user")
        if default_role:
            user.roles = [default_role]
            await self.user_repository.session.commit()
            await self.user_repository.session.refresh(user)
        else:
            # If no 'user' role exists, try 'basic' role
            basic_role = await self.role_repository.get_by_title("basic")
            if basic_role:
                user.roles = [basic_role]
                await self.user_repository.session.commit()
                await self.user_repository.session.refresh(user)
