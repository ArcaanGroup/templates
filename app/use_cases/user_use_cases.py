from typing import Optional

from fastapi_pagination import Page, Params

from app.error.exceptions import ConflictException, ResourceNotFoundException
from app.infrastructure.mappers import UserMapper
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models import User, UserCreate, UserUpdate


class UserUseCase:
    """Use case layer for user operations."""

    def __init__(
        self, user_repository: IUserRepository, role_repository: IRoleRepository
    ):
        self.user_repo = user_repository
        self.role_repo = role_repository

    async def get_all(self, params: Params) -> Page[User]:
        """Get all users and map domain models to DTOs."""
        user_domains_page = await self.user_repo.get_all(params)

        user_dtos = [
            UserMapper.to_dto(domain_user) for domain_user in user_domains_page.items
        ]
        user_domains_page.items = user_dtos  # pyright: ignore[reportAttributeAccessIssue]

        return user_domains_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, user_id: str) -> User:
        """Retrieve a user by ID."""
        domain_user = await self.user_repo.get_by_id(user_id)

        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        return UserMapper.to_dto(domain_user)

    async def create(self, user_create: UserCreate) -> User:
        """Create a new user with validation and uniqueness checks."""
        domain_user = UserMapper.from_dto(user_create)

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

        created_domain_user = await self.user_repo.create(domain_user)
        return UserMapper.to_dto(created_domain_user)

    async def update(self, user_id: str, update_dto: UserUpdate) -> User:
        """Update user metadata and ensure no uniqueness conflicts."""
        target_domain = await self.user_repo.get_by_id(user_id)

        if not target_domain:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

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

        return UserMapper.to_dto(updated_domain)

    async def delete(self, user_id: str) -> User:
        """Delete a user after verifying existence."""
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        deleted_domain_user = await self.user_repo.delete(user_id)
        if not deleted_domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        return UserMapper.to_dto(deleted_domain_user)

    async def assign_role(self, user_id: str, role_id: str) -> User:
        """Assign a role to an existing user."""
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        updated_domain_user = await self.user_repo.assign_role(user_id, role_id)
        return UserMapper.to_dto(updated_domain_user)

    async def remove_role(self, user_id: str, role_id: str) -> User:
        """Remove a role assignment from an existing user."""
        domain_user = await self.user_repo.get_by_id(user_id)
        if not domain_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        updated_domain_user = await self.user_repo.remove_role(user_id, role_id)
        return UserMapper.to_dto(updated_domain_user)
