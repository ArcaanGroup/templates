from typing import Optional

from fastapi_pagination import Page, Params

from app.core.config import config
from app.error.exceptions import ConflictException, ResourceNotFoundException
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.user.dto import User, UserCreate, UserUpdate
from app.models.user.mapper import UserMapper
from app.utils.pagination import extract_limit_skip_from_params


class UserService:
    """
    Service layer for user operations.
    Contains business logic for user management.
    """

    def __init__(
        self, user_repository: IUserRepository, role_repository: IRoleRepository
    ):
        self.user_repo = user_repository
        self.role_repo = role_repository

    async def get_all(self, params: Params) -> Page[User]:
        """Get all users with business logic."""
        user_domains_page = await self.user_repo.get_all(params)

        user_dtos: list[User] = []
        for domain_user in user_domains_page.items:
            user_dtos.append(UserMapper.to_dto(domain_user))

        user_domains_page.items = user_dtos  # pyright: ignore[reportAttributeAccessIssue]

        return user_domains_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, user_id: str) -> User:
        """Get a specific user by ID with business logic."""
        domain_user = await self.user_repo.get_by_id(user_id)

        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        return UserMapper.to_dto(domain_user)

    async def create(self, user_create: UserCreate) -> User:
        """Create a new user with business validation."""
        # Create domain entity from DTO to apply validation
        domain_user = UserMapper.from_dto(user_create)

        # Check if user with email or username already exists
        existing_user_by_email = await self.user_repo.get_by_email(user_create.email)
        if existing_user_by_email:
            raise ConflictException(
                f"User with email '{user_create.email}' already exists"
            )

        existing_user_by_username = await self.user_repo.get_by_username(
            user_create.username
        )
        if existing_user_by_username:
            raise ConflictException(
                f"User with username '{user_create.username}' already exists"
            )

        # Create user via repository
        created_domain_user = await self.user_repo.create(domain_user)

        return UserMapper.to_dto(created_domain_user)

    async def update(self, user_id: str, update_dto: UserUpdate) -> User:
        """Update a user with business validation."""
        # Get the current user to check for conflicts
        target_domain = await self.user_repo.get_by_id(user_id)

        if not target_domain:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Check if the new email or username conflicts with existing users (excluding current user)
        if update_dto.email and update_dto.email != target_domain.email:
            existing_user = await self.user_repo.get_by_email(update_dto.email)
            if existing_user and existing_user.id != user_id:
                raise ConflictException(
                    f"User with email '{update_dto.email}' already exists"
                )

        if update_dto.username and update_dto.username != target_domain.username:
            existing_user = await self.user_repo.get_by_username(update_dto.username)
            if existing_user and existing_user.id != user_id:
                raise ConflictException(
                    f"User with username '{update_dto.username}' already exists"
                )

        UserMapper.update_from_dto(update_dto, target_domain)

        updated_domain = await self.user_repo.update(target_domain)

        if updated_domain is None:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Return DTO representation
        return UserMapper.to_dto(updated_domain)

    async def delete(self, user_id: str) -> User:
        """Delete a user with business logic."""
        # Verify user exists before deletion
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Delete user via repository
        deleted_domain_user = await self.user_repo.delete(user_id)
        if not deleted_domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        return UserMapper.to_dto(deleted_domain_user)

    async def assign_role(self, user_id: str, role_id: str) -> User:
        """Assign a role to a user with business validation."""
        # Verify user exists
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Verify role exists
        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Assign role to user via repository
        updated_domain_user = await self.user_repo.assign_role(user_id, role_id)

        return UserMapper.to_dto(updated_domain_user)

    async def remove_role(self, user_id: str, role_id: str) -> User:
        """Remove a role from a user with business validation."""
        # Verify user exists
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Verify role exists
        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Remove role from user via repository
        updated_domain_user = await self.user_repo.remove_role(user_id, role_id)

        return UserMapper.to_dto(updated_domain_user)
