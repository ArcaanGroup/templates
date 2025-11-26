"""Delete user use case"""
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.user_exceptions import UserNotFoundException


class DeleteUserUseCase:
    """Use case for deleting a user"""

    def __init__(
        self,
        repository: UserRepositoryInterface,
        cache: CacheInterface
    ):
        self.repository = repository
        self.cache = cache

    async def execute(self, user_id: int) -> None:
        """Execute the delete user use case"""
        # Get the user to check if it exists
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Delete the user
        await self.repository.delete(user)

        # Invalidate cache
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)
