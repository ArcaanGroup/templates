"""Role service for business logic operations"""

from typing import Optional, List
import uuid

from app.infrastructure.database.models.role import RoleModel
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.application.dto.auth_dto import UserDTO


class RoleService:
    """Service class for role business logic"""

    def __init__(self, role_repository: SQLAlchemyRoleRepository):
        self.role_repository = role_repository

    async def get_user_roles(self, user_id: int) -> List[RoleModel]:
        """Get all roles for a specific user"""
        return await self.role_repository.get_user_roles(user_id)

    async def get_role_by_title(self, title: str) -> Optional[RoleModel]:
        """Get role by title"""
        return await self.role_repository.get_by_title(title)

    async def get_role_by_id(self, role_id: uuid.UUID) -> Optional[RoleModel]:
        """Get role by ID"""
        return await self.role_repository.get_by_id(str(role_id))
