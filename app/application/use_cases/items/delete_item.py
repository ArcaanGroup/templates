"""Delete item use case"""
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import ItemRepositoryInterface
from app.domain.exceptions.item_exceptions import ItemNotFoundException


class DeleteItemUseCase:
    """Use case for deleting an item"""
    
    def __init__(
        self,
        repository: ItemRepositoryInterface,
        cache: CacheInterface | None = None
    ):
        self.repository = repository
        self.cache = cache
    
    async def execute(self, item_id: int) -> None:
        """Execute the delete item use case"""
        # Get existing item
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(item_id)
        
        # Delete item
        await self.repository.delete(item)
        
        # Invalidate cache
        if self.cache and item.id:
            cache_key = f"item:{item.id}"
            await self.cache.delete(cache_key)

