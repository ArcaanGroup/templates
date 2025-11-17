"""FastAPI dependencies"""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import ItemRepositoryInterface
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.items.create_item import CreateItemUseCase
from app.application.use_cases.items.delete_item import DeleteItemUseCase
from app.application.use_cases.items.get_item import GetItemUseCase
from app.application.use_cases.items.list_items import ListItemsUseCase
from app.application.use_cases.items.update_item import UpdateItemUseCase
from app.infrastructure.cache.memory_cache import MemoryCache
from app.infrastructure.database.session import get_db
from app.infrastructure.messaging.event_bus import InMemoryEventBus
from app.infrastructure.repositories.item_repository import SQLAlchemyItemRepository


# Cache singleton
_cache: CacheInterface | None = None


def get_cache() -> CacheInterface:
    """Get cache instance"""
    global _cache
    if _cache is None:
        _cache = MemoryCache()
    return _cache


# Event bus singleton
_event_bus: EventBusInterface | None = None


def get_event_bus() -> EventBusInterface:
    """Get event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
        # Register event handlers
        from app.application.events.handlers import handle_item_created
        from app.domain.events.item_created import ItemCreatedEvent
        # Note: In a real app, this would be done at startup
    return _event_bus


def get_item_repository(
    db: AsyncSession = Depends(get_db)
) -> ItemRepositoryInterface:
    """Get item repository"""
    return SQLAlchemyItemRepository(db)


def get_create_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    event_bus: EventBusInterface = Depends(get_event_bus)
) -> CreateItemUseCase:
    """Get create item use case"""
    return CreateItemUseCase(repository, event_bus)


def get_get_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache)
) -> GetItemUseCase:
    """Get get item use case"""
    return GetItemUseCase(repository, cache)


def get_list_items_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository)
) -> ListItemsUseCase:
    """Get list items use case"""
    return ListItemsUseCase(repository)


def get_update_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache)
) -> UpdateItemUseCase:
    """Get update item use case"""
    return UpdateItemUseCase(repository, cache)


def get_delete_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache)
) -> DeleteItemUseCase:
    """Get delete item use case"""
    return DeleteItemUseCase(repository, cache)


def get_login_use_case() -> LoginUseCase:
    """Get login use case"""
    return LoginUseCase()

