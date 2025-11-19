"""Create item use case"""
from app.application.dto.item_dto import ItemCreateDTO, ItemDTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import ItemRepositoryInterface
from app.domain.entities.item import Item
from app.domain.events.item_created import ItemCreatedEvent


class CreateItemUseCase:
    """Use case for creating an item"""
    
    def __init__(
        self,
        repository: ItemRepositoryInterface,
        event_bus: EventBusInterface
    ):
        self.repository = repository
        self.event_bus = event_bus
    
    async def execute(self, dto: ItemCreateDTO) -> ItemDTO:
        """Execute the create item use case"""
        # Create domain entity
        item = Item(
            name=dto.name,
            price=dto.price,
            is_offer=dto.is_offer
        )
        
        # Persist entity
        created_item = await self.repository.create(item)
        
        # Publish domain event
        event = ItemCreatedEvent(
            item_id=created_item.id,
            name=created_item.name,
            price=created_item.price
        )
        await self.event_bus.publish(event)
        
        # Convert to DTO
        return ItemDTO(
            id=created_item.id,
            name=created_item.name,
            price=created_item.price,
            is_offer=created_item.is_offer,
            created_at=created_item.created_at,
            updated_at=created_item.updated_at
        )

