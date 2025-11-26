"""Get role use case"""
import uuid

from app.application.dto.role_dto import RoleDTO
from app.application.interfaces.repositories import RoleRepositoryInterface
from app.domain.exceptions import EntityNotFoundException


class GetRoleUseCase:
    """Use case for getting a role by ID"""

    def __init__(self, repository: RoleRepositoryInterface):
        self._repository = repository

    async def execute(self, role_id: uuid.UUID) -> RoleDTO:
        """Execute the use case to get a role by ID"""
        role = await self._repository.get_by_id(role_id)

        if not role:
            raise EntityNotFoundException("Role", str(role_id))

        return RoleDTO(
            id=role.id,
            title=role.title,
            description=role.description,
            permissions=role.permissions,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
