"""Item repository implementation"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import ItemRepositoryInterface
from app.domain.entities.item import Item
from app.infrastructure.database.models.item import ItemModel


class SQLAlchemyItemRepository(ItemRepositoryInterface):
    """SQLAlchemy implementation of ItemRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: ItemModel) -> Item:
        """Convert ORM model to domain entity"""
        return Item(
            id=model.id,
            name=model.name,
            price=model.price,
            is_offer=model.is_offer,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Item) -> ItemModel:
        """Convert domain entity to ORM model"""
        return ItemModel(
            id=entity.id, name=entity.name, price=entity.price, is_offer=entity.is_offer
        )

    async def create(self, entity: Item) -> Item:
        """Create a new item"""
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, id: int) -> Optional[Item]:
        """Get item by ID"""
        result = await self.session.execute(select(ItemModel).where(ItemModel.id == id))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """List all items with pagination"""
        result = await self.session.execute(
            select(ItemModel).offset(skip).limit(limit).order_by(ItemModel.id)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def update(self, entity: Item) -> Item:
        """Update an item"""
        result = await self.session.execute(select(ItemModel).where(ItemModel.id == entity.id))
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Item with id {entity.id} not found")

        model.name = entity.name
        model.price = entity.price
        model.is_offer = entity.is_offer

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: Item) -> None:
        """Delete an item"""
        result = await self.session.execute(select(ItemModel).where(ItemModel.id == entity.id))
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Item with id {entity.id} not found")

        await self.session.delete(model)
        await self.session.commit()
