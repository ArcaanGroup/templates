"""Get current user use case"""

from app.application.dto.auth_dto import UserDTO
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.auth_exceptions import UserNotFoundException
from app.domain.services.auth_service import TokenService


class GetCurrentUserUseCase:
    """Use case for getting current user information"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, token: str) -> UserDTO:
        """Execute the get current user use case"""
        username = TokenService.decode_access_token(token)
        if not username:
            raise UserNotFoundException("Invalid token")

        user = await self.user_repository.get_by_username(username)
        if not user:
            raise UserNotFoundException(username)

        # Convert domain user to DTO
        return UserDTO(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
