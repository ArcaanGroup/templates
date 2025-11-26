"""List roles use case"""
from typing import List

from app.application.dto.role_dto import RoleDTO
from app.application.interfaces.repositories import RoleRepositoryInterface


class ListRolesUseCase:
    """Use case for listing all roles"""

    def __init__(self, repository: RoleRepositoryInterface):
        self._repository = repository

    async def execute(self) -> List[RoleDTO]:
        """Execute the use case to list all roles"""
        roles = await self._repository.list_all()

        return [
            RoleDTO(
                id=role.id,
                title=role.title,
                description=role.description,
                permissions=role.permissions,
                created_at=role.created_at,
                updated_at=role.updated_at
            )
            for role in roles
        ]
