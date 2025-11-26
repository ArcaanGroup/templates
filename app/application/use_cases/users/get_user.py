"""Get user by ID use case"""
from app.application.dto.auth_dto import UserDTO
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.auth_exceptions import UserNotFoundException


class GetUserUseCase:
    """Use case for getting a user by ID"""

    def __init__(
        self,
        repository: UserRepositoryInterface,
        cache: CacheInterface
    ):
        self.repository = repository
        self.cache = cache

    async def execute(self, user_id: int) -> UserDTO:
        """Execute the get user by ID use case"""
        # Try to get from cache first
        cache_key = f"user:{user_id}"
        cached_user = await self.cache.get(cache_key)
        if cached_user:
            return UserDTO.model_validate(cached_user)

        # If not in cache, fetch from repository
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Convert to DTO - get role titles for the response
        role_titles = [role.title.value for role in user.roles]

        # Convert to DTO
        user_dto = UserDTO(
            id=user.id,
            username=user.username.value,
            email=user.email.value,
            is_active=user.is_active,
            roles=role_titles,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        # Store in cache for future requests
        await self.cache.set(cache_key, user_dto.model_dump(), ttl=300)  # Cache for 5 minutes

        return user_dto
