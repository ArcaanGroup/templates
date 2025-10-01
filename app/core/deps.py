from typing import Annotated
from fastapi import Depends, Request

from app.repositories.items_repository import ItemsRepository
from app.services.items_service import ItemsService


def get_items_repo(request: Request) -> ItemsRepository:
    """
    Provide the app-scoped ItemsRepository instance.
    It's created in app.main's lifespan and stored on app.state.
    """
    return request.app.state.items_repo  # type: ignore[attr-defined]


def get_items_service(
    repo: Annotated[ItemsRepository, Depends(get_items_repo)],
) -> ItemsService:
    """
    Construct the ItemsService by injecting the repository.
    Keeping this as a dependency makes tests easy to override.
    """
    return ItemsService(repo)
