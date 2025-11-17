"""Update item use case"""
from app.application.dto.item_dto import ItemDTO, ItemUpdateDTO
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import ItemRepositoryInterface
from app.domain.exceptions.item_exceptions import ItemNotFoundException


class UpdateItemUseCase:
    """Use case for updating an item"""
    
    def __init__(
        self,
        repository: ItemRepositoryInterface,
        cache: CacheInterface | None = None
    ):
        self.repository = repository
        self.cache = cache
    
    async def execute(self, item_id: int, dto: ItemUpdateDTO) -> ItemDTO:
        """Execute the update item use case"""
        # Get existing item
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(item_id)
        
        # Update item properties
        if dto.name is not None:
            item.update_name(dto.name)
        if dto.price is not None:
            item.update_price(dto.price)
        if dto.is_offer is not None:
            item.set_offer(dto.is_offer)
        
        # Persist changes
        updated_item = await self.repository.update(item)
        
        # Invalidate cache
        if self.cache and updated_item.id:
            cache_key = f"item:{updated_item.id}"
            await self.cache.delete(cache_key)
        
        # Convert to DTO
        return ItemDTO(
            id=updated_item.id,
            name=updated_item.name,
            price=updated_item.price,
            is_offer=updated_item.is_offer,
            created_at=updated_item.created_at,
            updated_at=updated_item.updated_at
        )

