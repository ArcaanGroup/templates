"""Register use case"""

from app.application.dto.auth_dto import RegisterDTO, TokenDTO, UserDTO
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.auth_exceptions import UserAlreadyExistsException
from app.domain.services.auth_service import TokenService, UserService


class RegisterUseCase:
    """Use case for user registration"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, dto: RegisterDTO) -> TokenDTO:
        """Execute the user registration use case"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_username(dto.username)
        if existing_user:
            raise UserAlreadyExistsException(dto.username)

        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user:
            raise UserAlreadyExistsException(dto.email)

        # Create the domain user
        user = UserService.create_user(
            username=dto.username, email=dto.email, password=dto.password
        )

        # Save the user
        created_user = await self.user_repository.create(user)

        # Create access token
        access_token = TokenService.create_access_token(subject=created_user.username.value)

        return TokenDTO(access_token=access_token, token_type="bearer")
