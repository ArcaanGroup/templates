"""List items use case"""
from fastapi_pagination import Page, Params, create_page

from app.application.dto.item_dto import ItemDTO
from app.application.interfaces.repositories import ItemRepositoryInterface


class ListItemsUseCase:
    """Use case for listing items with pagination"""
    
    def __init__(self, repository: ItemRepositoryInterface):
        self.repository = repository
    
    async def execute(self, params: Params) -> Page[ItemDTO]:
        """Execute the list items use case"""
        # Get items from repository
        items = await self.repository.list_all(skip=params.offset, limit=params.size)
        
        # Convert to DTOs
        dtos = [
            ItemDTO(
                id=item.id,
                name=item.name,
                price=item.price,
                is_offer=item.is_offer,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            for item in items
        ]
        
        # Create paginated response
        # Note: This is a simplified version. In production, you'd want
        # proper pagination support from the repository with total count
        total = len(items)  # In real implementation, get total from repository
        return create_page(dtos, total=total, params=params)

