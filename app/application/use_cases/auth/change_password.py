"""Change password use case"""

from app.application.dto.auth_dto import PasswordChangeDTO
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.services.auth_service import PasswordService


class ChangePasswordUseCase:
    """Use case for changing user password"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, user_id: int, dto: PasswordChangeDTO) -> bool:
        """Execute the password change use case"""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise AuthenticationFailedException("User not found")

        # Verify current password
        if not user.verify_password(dto.current_password):
            raise AuthenticationFailedException("Current password is incorrect")

        # Update password
        from app.domain.value_objects.password import Password

        new_password = Password(dto.new_password)
        user.update_password(new_password)

        # Save updated user
        await self.user_repository.update(user)

        return True
