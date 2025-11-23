"""List items use case"""

from fastapi_pagination import Page, Params, create_page

from app.application.dto.item_dto import ItemDTO
from app.application.interfaces.repositories import ItemRepositoryInterface


class ListItemsUseCase:
    """Use case for listing items with pagination"""

    def __init__(self, repository: ItemRepositoryInterface):
        self.repository = repository

    async def execute(self, params: Params) -> Page[ItemDTO]:
        """Execute the list items use case with proper enterprise pagination"""
        # Convert params to raw params for offset and limit
        raw_params = params.to_raw_params()

        # Get items from repository
        items = await self.repository.list_all(skip=raw_params.offset, limit=raw_params.limit)

        # Count total items for proper pagination
        total = await self.repository.count_all()

        # Convert to DTOs
        dtos = [
            ItemDTO(
                id=item.id,
                name=item.name,
                price=item.price,
                is_offer=item.is_offer,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]

        # Create paginated response with correct total count
        return create_page(dtos, total=total, params=params)
