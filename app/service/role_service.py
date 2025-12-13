from typing import List

from fastapi_pagination import Page, Params

from app.error.exceptions import ResourceNotFoundException
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.models.role.domain import RoleDomain
from app.models.role.dto import Role, RoleCreate, RoleUpdate
from app.models.role.mapper import RoleMapper
from app.service.permission_service import PermissionService


class RoleService:
    """
    Service layer for role operations.
    Contains business logic for role management.
    """

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_service: PermissionService,
    ):
        self.role_repo = role_repository
        self.permission_service = permission_service

    async def get_all(self, params: Params) -> Page[Role]:
        """Get all roles with business logic."""
        roles_page = await self.role_repo.get_all(params)

        role_dtos = [RoleMapper.to_dto(role_domain) for role_domain in roles_page.items]

        roles_page.items = role_dtos  # pyright: ignore[reportAttributeAccessIssue]

        return roles_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, role_id: str) -> Role:
        """Get a specific role by ID with business logic."""
        domain_role = await self.role_repo.get_by_id(role_id)

        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(domain_role)

    async def create(self, role_create: RoleCreate) -> Role:
        """Create a new role with business validation."""
        # Validate permission IDs if provided and get the cleaned list
        final_permission_ids = role_create.permission_ids
        if role_create.permission_ids:
            final_permission_ids = await self._validate_permission_ids(
                role_create.permission_ids
            )

        # Create domain entity first to validate business rules
        domain_role = RoleDomain.create(
            name=role_create.name,  # Default field, change as needed
            permission_ids=final_permission_ids,
        )

        # Create role via repository
        created_domain_role = await self.role_repo.create(domain_role)

        return RoleMapper.to_dto(created_domain_role)

    async def update(self, role_id: str, role_update: RoleUpdate) -> Role:
        """Update a role with business validation."""
        # Get the current role
        role_domain = await self.role_repo.get_by_id(role_id)

        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Validate permission IDs if provided in the update and get the cleaned list
        if role_update.permission_ids is not None:
            if role_update.permission_ids:
                cleaned_permission_ids = await self._validate_permission_ids(
                    role_update.permission_ids
                )
                role_update.permission_ids = cleaned_permission_ids
            else:
                # If permission_ids is an empty list, still process it to remove duplicates if any
                role_update.permission_ids = []

        # Update the domain entity using its business methods
        RoleMapper.update_from_dto(role_update, role_domain)

        # Update via repository
        updated_domain_role = await self.role_repo.update(role_domain)
        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def assign_permission_to_role(self, role_id: str, permission_id: str) -> Role:
        """Assign a permission to a role."""
        # Validate that the permission exists
        await self._validate_permission_ids([permission_id])

        # Get the role
        role_domain = await self.role_repo.get_by_id(role_id)
        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Add the permission if not already assigned
        if permission_id not in (role_domain.permission_ids or []):
            if role_domain.permission_ids:
                role_domain.permission_ids.append(permission_id)
            else:
                role_domain.permission_ids = [permission_id]

        # Update the role via repository
        updated_domain_role = await self.role_repo.update(role_domain)
        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def remove_permission_from_role(
        self, role_id: str, permission_id: str
    ) -> Role:
        """Remove a permission from a role."""
        # Get the role
        role_domain = await self.role_repo.get_by_id(role_id)
        if not role_domain:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Remove the permission if it exists
        if role_domain.permission_ids and permission_id in role_domain.permission_ids:
            role_domain.permission_ids = [
                pid for pid in role_domain.permission_ids if pid != permission_id
            ]

        # Update the role via repository
        updated_domain_role = await self.role_repo.update(role_domain)
        if not updated_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(updated_domain_role)

    async def _validate_permission_ids(self, permission_ids: List[str]) -> List[str]:
        """Validate that all provided permission IDs exist in the permissions JSON file and remove duplicates."""
        # Remove duplicates while preserving order
        seen = set()
        unique_permission_ids = []
        for perm_id in permission_ids:
            if perm_id not in seen:
                seen.add(perm_id)
                unique_permission_ids.append(perm_id)

        # Get all permissions
        all_permissions = await self.permission_service.get_all_permissions()

        # Create a set of available permission IDs for efficient lookup
        available_permission_ids = {perm.id for perm in all_permissions}

        # Check each requested permission ID
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

    async def delete(self, role_id: str) -> Role:
        """Delete a role with business logic."""
        # Verify role exists before deletion
        domain_role = await self.role_repo.get_by_id(role_id)
        if not domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        deleted_domain_role = await self.role_repo.delete(domain_role.id)
        if not deleted_domain_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        return RoleMapper.to_dto(deleted_domain_role)
