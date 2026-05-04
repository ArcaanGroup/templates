"""
True Clean Architecture Use Cases for Role operations.
Use cases contain business logic and are independent of frameworks and external concerns.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from app.domain.entities import RoleEntity
from app.domain.error.exceptions import ResourceNotFoundException
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)
from app.interface.repository.role_repository_interface import IRoleRepository


@dataclass(frozen=True)
class GetAllRolesRequest:
    """Input port for getting all roles."""
    page: int = 1
    size: int = 20


@dataclass(frozen=True)
class GetAllRolesResponse:
    """Output port for getting all roles."""
    roles: List[RoleEntity]
    total: int
    page: int
    size: int


@dataclass(frozen=True)
class GetRoleByIdRequest:
    """Input port for getting a role by ID."""
    role_id: str


@dataclass(frozen=True)
class GetRoleByIdResponse:
    """Output port for getting a role by ID."""
    role: RoleEntity


@dataclass(frozen=True)
class CreateRoleRequest:
    """Input port for creating a role."""
    name: str
    permission_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class CreateRoleResponse:
    """Output port for creating a role."""
    role: RoleEntity


@dataclass(frozen=True)
class UpdateRoleRequest:
    """Input port for updating a role."""
    role_id: str
    name: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[str]] = None


@dataclass(frozen=True)
class UpdateRoleResponse:
    """Output port for updating a role."""
    role: RoleEntity


@dataclass(frozen=True)
class DeleteRoleRequest:
    """Input port for deleting a role."""
    role_id: str


@dataclass(frozen=True)
class DeleteRoleResponse:
    """Output port for deleting a role."""
    role: RoleEntity


@dataclass(frozen=True)
class AssignPermissionRequest:
    """Input port for assigning a permission to a role."""
    role_id: str
    permission_id: str


@dataclass(frozen=True)
class AssignPermissionResponse:
    """Output port for assigning a permission to a role."""
    role: RoleEntity


@dataclass(frozen=True)
class RemovePermissionRequest:
    """Input port for removing a permission from a role."""
    role_id: str
    permission_id: str


@dataclass(frozen=True)
class RemovePermissionResponse:
    """Output port for removing a permission from a role."""
    role: RoleEntity


class GetAllRolesUseCase:
    """Use case for retrieving all roles."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repo = role_repository

    async def execute(self, request: GetAllRolesRequest) -> GetAllRolesResponse:
        """Execute the use case to get all roles."""
        roles = await self._role_repo.get_all()
        return GetAllRolesResponse(
            roles=roles,
            total=len(roles),
            page=request.page,
            size=request.size,
        )


class GetRoleByIdUseCase:
    """Use case for retrieving a role by ID."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repo = role_repository

    async def execute(self, request: GetRoleByIdRequest) -> GetRoleByIdResponse:
        """Execute the use case to get a role by ID."""
        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )
        return GetRoleByIdResponse(role=role)


class CreateRoleUseCase:
    """Use case for creating a new role."""

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
    ):
        self._role_repo = role_repository
        self._permission_repo = permission_repository

    async def execute(self, request: CreateRoleRequest) -> CreateRoleResponse:
        """Execute the use case to create a new role."""
        # Validate permission IDs if provided
        if request.permission_ids:
            await self._validate_permission_ids(request.permission_ids)

        # Create role entity using domain factory method
        role = RoleEntity.create(
            name=request.name,
            permission_ids=request.permission_ids,
        )

        created_role = await self._role_repo.create(role)
        return CreateRoleResponse(role=created_role)

    async def _validate_permission_ids(self, permission_ids: List[str]) -> None:
        """Validate that all permission IDs exist."""
        seen = set()
        unique_ids = []
        for perm_id in permission_ids:
            if perm_id not in seen:
                seen.add(perm_id)
                unique_ids.append(perm_id)

        all_permissions = await self._permission_repo.get_all()
        available_ids = {perm.id for perm in all_permissions}

        invalid_ids = [pid for pid in unique_ids if pid not in available_ids]
        if invalid_ids:
            raise ResourceNotFoundException(
                resource_type="Permission", identifier=f"{invalid_ids}"
            )


class UpdateRoleUseCase:
    """Use case for updating a role."""

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
    ):
        self._role_repo = role_repository
        self._permission_repo = permission_repository

    async def execute(self, request: UpdateRoleRequest) -> UpdateRoleResponse:
        """Execute the use case to update a role."""
        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        # Validate permission IDs if provided
        if request.permission_ids is not None:
            if request.permission_ids:
                await self._validate_permission_ids(request.permission_ids)
            else:
                request.permission_ids = []

        # Update role using domain method
        role.update_info(
            name=request.name,
            is_active=request.is_active,
            permission_ids=request.permission_ids,
        )

        updated_role = await self._role_repo.update(role)
        if not updated_role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        return UpdateRoleResponse(role=updated_role)

    async def _validate_permission_ids(self, permission_ids: List[str]) -> None:
        """Validate that all permission IDs exist."""
        seen = set()
        unique_ids = []
        for perm_id in permission_ids:
            if perm_id not in seen:
                seen.add(perm_id)
                unique_ids.append(perm_id)

        all_permissions = await self._permission_repo.get_all()
        available_ids = {perm.id for perm in all_permissions}

        invalid_ids = [pid for pid in unique_ids if pid not in available_ids]
        if invalid_ids:
            raise ResourceNotFoundException(
                resource_type="Permission", identifier=f"{invalid_ids}"
            )


class DeleteRoleUseCase:
    """Use case for deleting a role."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repo = role_repository

    async def execute(self, request: DeleteRoleRequest) -> DeleteRoleResponse:
        """Execute the use case to delete a role."""
        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        deleted_role = await self._role_repo.delete(role.id)
        if not deleted_role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        return DeleteRoleResponse(role=deleted_role)


class AssignPermissionToRoleUseCase:
    """Use case for assigning a permission to a role."""

    def __init__(
        self,
        role_repository: IRoleRepository,
        permission_repository: IPermissionRepository,
    ):
        self._role_repo = role_repository
        self._permission_repo = permission_repository

    async def execute(self, request: AssignPermissionRequest) -> AssignPermissionResponse:
        """Execute the use case to assign a permission to a role."""
        # Verify permission exists
        await self._validate_permission_ids([request.permission_id])

        # Get role
        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        # Add permission if not already assigned
        role.permission_ids = role.permission_ids or []
        if request.permission_id not in role.permission_ids:
            role.permission_ids.append(request.permission_id)

        updated_role = await self._role_repo.update(role)
        if not updated_role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        return AssignPermissionResponse(role=updated_role)

    async def _validate_permission_ids(self, permission_ids: List[str]) -> None:
        """Validate that all permission IDs exist."""
        all_permissions = await self._permission_repo.get_all()
        available_ids = {perm.id for perm in all_permissions}

        invalid_ids = [pid for pid in permission_ids if pid not in available_ids]
        if invalid_ids:
            raise ResourceNotFoundException(
                resource_type="Permission", identifier=f"{invalid_ids}"
            )


class RemovePermissionFromRoleUseCase:
    """Use case for removing a permission from a role."""

    def __init__(self, role_repository: IRoleRepository):
        self._role_repo = role_repository

    async def execute(
        self, request: RemovePermissionRequest
    ) -> RemovePermissionResponse:
        """Execute the use case to remove a permission from a role."""
        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        # Remove permission
        role.permission_ids = [
            pid for pid in (role.permission_ids or []) if pid != request.permission_id
        ]

        updated_role = await self._role_repo.update(role)
        if not updated_role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        return RemovePermissionResponse(role=updated_role)
