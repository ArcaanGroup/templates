"""FastAPI dependencies"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import ItemRepositoryInterface, UserRepositoryInterface
from app.application.use_cases.auth.change_password import ChangePasswordUseCase
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.items.create_item import CreateItemUseCase
from app.application.use_cases.items.delete_item import DeleteItemUseCase
from app.application.use_cases.items.get_item import GetItemUseCase
from app.application.use_cases.items.list_items import ListItemsUseCase
from app.application.use_cases.items.update_item import UpdateItemUseCase
from app.application.dto.auth_dto import UserDTO
from app.core.security import oauth2_scheme, get_current_user
from app.infrastructure.cache.memory_cache import MemoryCache
from app.infrastructure.database.session import get_db
from app.infrastructure.messaging.event_bus import InMemoryEventBus
from app.infrastructure.repositories.item_repository import SQLAlchemyItemRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository


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


def get_item_repository(db: AsyncSession = Depends(get_db)) -> ItemRepositoryInterface:
    """Get item repository"""
    return SQLAlchemyItemRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryInterface:
    """Get user repository"""
    return SQLAlchemyUserRepository(db)


def get_create_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    event_bus: EventBusInterface = Depends(get_event_bus),
) -> CreateItemUseCase:
    """Get create item use case"""
    return CreateItemUseCase(repository, event_bus)


def get_get_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache),
) -> GetItemUseCase:
    """Get get item use case"""
    return GetItemUseCase(repository, cache)


def get_list_items_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
) -> ListItemsUseCase:
    """Get list items use case"""
    return ListItemsUseCase(repository)


def get_update_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache),
) -> UpdateItemUseCase:
    """Get update item use case"""
    return UpdateItemUseCase(repository, cache)


def get_delete_item_use_case(
    repository: ItemRepositoryInterface = Depends(get_item_repository),
    cache: CacheInterface = Depends(get_cache),
) -> DeleteItemUseCase:
    """Get delete item use case"""
    return DeleteItemUseCase(repository, cache)


def get_login_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> LoginUseCase:
    """Get login use case"""
    return LoginUseCase(user_repository)


def get_register_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> RegisterUseCase:
    """Get register use case"""
    return RegisterUseCase(user_repository)


def get_current_user_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    """Get get current user use case"""
    return GetCurrentUserUseCase(user_repository)


def get_change_password_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> ChangePasswordUseCase:
    """Get change password use case"""
    return ChangePasswordUseCase(user_repository)


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> UserDTO:
    """Get current user DTO from token"""
    return await use_case.execute(token)
