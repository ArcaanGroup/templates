"""Get item use case"""
from app.application.dto.item_dto import ItemDTO
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import ItemRepositoryInterface
from app.domain.exceptions.item_exceptions import ItemNotFoundException


class GetItemUseCase:
    """Use case for getting an item by ID"""
    
    def __init__(
        self,
        repository: ItemRepositoryInterface,
        cache: CacheInterface | None = None
    ):
        self.repository = repository
        self.cache = cache
    
    async def execute(self, item_id: int) -> ItemDTO:
        """Execute the get item use case"""
        # Try cache first
        if self.cache:
            cache_key = f"item:{item_id}"
            cached = await self.cache.get(cache_key)
            if cached:
                return ItemDTO(**cached)
        
        # Get from repository
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(item_id)
        
        # Convert to DTO
        dto = ItemDTO(
            id=item.id,
            name=item.name,
            price=item.price,
            is_offer=item.is_offer,
            created_at=item.created_at,
            updated_at=item.updated_at
        )
        
        # Cache the result
        if self.cache and item.id:
            cache_key = f"item:{item.id}"
            await self.cache.set(cache_key, dto.model_dump(), ttl=300)
        
        return dto

