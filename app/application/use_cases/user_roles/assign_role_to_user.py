"""Use case for assigning roles to a user"""

from typing import List
import uuid
from app.application.dto.user_role_dto import UserRoleAssignmentDTO
from app.application.interfaces.repositories import UserRepositoryInterface, RoleRepositoryInterface
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.exceptions.user_exceptions import UserNotFoundException


class AssignRoleToUserUseCase:
    """Use case for assigning roles to a user"""

    def __init__(self, user_repository: UserRepositoryInterface, role_repository: RoleRepositoryInterface):
        self._user_repository = user_repository
        self._role_repository = role_repository

    async def execute(self, dto: UserRoleAssignmentDTO) -> User:
        """Assign roles to a user"""
        # Get the user
        user = await self._user_repository.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {dto.user_id} not found")

        # Get the roles by their IDs
        roles: List[Role] = []
        for role_id in dto.role_ids:
            role = await self._role_repository.get_by_id(role_id)
            if role:
                roles.append(role)
            else:
                # Optionally raise an exception if a role doesn't exist
                from app.domain.exceptions.role_exceptions import RoleNotFoundException
                raise RoleNotFoundException(f"Role with ID {role_id} not found")

        # Update user roles
        user.update_roles(roles)

        # Save the user
        updated_user = await self._user_repository.update(user)
        return updated_user
