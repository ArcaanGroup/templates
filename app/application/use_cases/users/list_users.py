"""List users use case"""
from fastapi_pagination import Page, Params, create_page

from app.application.dto.auth_dto import UserDTO
from app.application.interfaces.repositories import UserRepositoryInterface


class ListUsersUseCase:
    """Use case for listing users with pagination"""

    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def execute(self, params: Params) -> Page[UserDTO]:
        """Execute the list users use case with proper enterprise pagination"""
        # Convert params to raw params for offset and limit
        raw_params = params.to_raw_params()

        # Get users from repository
        users = await self.repository.list_all(skip=raw_params.offset, limit=raw_params.limit)

        # Count total users for proper pagination
        total = await self.repository.count_all()

        # Convert to DTOs
        dtos = [
            UserDTO(
                id=user.id,
                username=user.username.value,
                email=user.email.value,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]

        # Create paginated response with correct total count
        return create_page(dtos, total=total, params=params)
