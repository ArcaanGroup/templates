"""Use case for getting a user's roles"""

from app.application.dto.user_role_dto import UserWithRolesDTO
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.entities.user import User
from app.domain.exceptions.user_exceptions import UserNotFoundException


class GetUserRolesUseCase:
    """Use case for getting a user's roles"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self._user_repository = user_repository

    async def execute(self, user_id: int) -> UserWithRolesDTO:
        """Get a user's roles"""
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Create DTO with user info and role titles
        role_titles = [role.title.value for role in user.roles]

        return UserWithRolesDTO(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            is_active=user.is_active,
            roles=role_titles
        )
