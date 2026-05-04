from typing import List

from fastapi_pagination import Page, Params

from app.application.mappers import RoleMapper
from app.domain.entities import RoleEntity
from app.domain.error.exceptions import ResourceNotFoundException
from app.interface.dto import Role, RoleCreate, RoleUpdate
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)
from app.interface.repository.role_repository_interface import IRoleRepository


class RoleUseCase:
    """Use case layer for role operations."""

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
    ):
        self.role_repo = role_repository
        self.permission_repository = permission_repository

    async def get_all(self, params: Params) -> Page[Role]:
        """Get all roles and map them to DTOs."""
        roles_page = await self.role_repo.get_all(params)
        role_dtos = [RoleMapper.to_dto(role_domain) for role_domain in roles_page.items]
        roles_page.items = role_dtos  # pyright: ignore[reportAttributeAccessIssue]
        return roles_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, role_id: str) -> Role:
        """Get a specific role by ID."""
        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)
        return RoleMapper.to_dto(domain_role)

    async def create(self, role_create: RoleCreate) -> Role:
        """Create a role with validated permissions."""
        final_permission_ids = role_create.permission_ids
        if role_create.permission_ids:
            final_permission_ids = await self._validate_permission_ids(
                role_create.permission_ids
            )

        domain_role = RoleEntity.create(
            name=role_create.name,
            permission_ids=final_permission_ids,
        )

        created_domain_role = await self.role_repo.create(domain_role)
        return RoleMapper.to_dto(created_domain_role)

    async def update(self, role_id: str, role_update: RoleUpdate) -> Role:
        """Update a role and maintain permission validation."""
        role_domain = await self.role_repo.get_by_id(role_id)
        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        if role_update.permission_ids is not None:
            if role_update.permission_ids:
                cleaned_permission_ids = await self._validate_permission_ids(
                    role_update.permission_ids
                )
                role_update.permission_ids = cleaned_permission_ids
            else:
                role_update.permission_ids = []

        RoleMapper.update_from_dto(role_update, role_domain)
        updated_domain_role = await self.role_repo.update(role_domain)

        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> Role:
        """Assign a permission to an existing role."""
        await self._validate_permission_ids([permission_id])

        role_domain = await self.role_repo.get_by_id(role_id)
        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        role_domain.permission_ids = role_domain.permission_ids or []
        if permission_id not in role_domain.permission_ids:
            role_domain.permission_ids.append(permission_id)

        updated_domain_role = await self.role_repo.update(role_domain)
        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def remove_permission_from_role(
        self, role_id: str, permission_id: str
    ) -> Role:
        """Remove a permission from a role."""
        role_domain = await self.role_repo.get_by_id(role_id)
        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        role_domain.permission_ids = [
            pid for pid in (role_domain.permission_ids or []) if pid != permission_id
        ]

        updated_domain_role = await self.role_repo.update(role_domain)
        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def delete(self, role_id: str) -> Role:
        """Delete a role after checking existence."""
        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        deleted_domain_role = await self.role_repo.delete(domain_role.id)
        if not deleted_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(deleted_domain_role)

    async def _validate_permission_ids(self, permission_ids: List[str]) -> List[str]:
        """Validate permission IDs and remove duplicates."""
        seen = set()
        unique_permission_ids = []
        for perm_id in permission_ids:
            if perm_id not in seen:
                seen.add(perm_id)
                unique_permission_ids.append(perm_id)

        all_permissions = await self.permission_repository.get_all()
        available_permission_ids = {perm.id for perm in all_permissions}

        invalid_permission_ids = [
            perm_id
            for perm_id in unique_permission_ids
            if perm_id not in available_permission_ids
        ]

        if invalid_permission_ids:
            raise ResourceNotFoundException(
                resource_type="Permission", identifier=f"{invalid_permission_ids}"
            )

        return unique_permission_ids
