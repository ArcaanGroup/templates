from typing import Annotated
from fastapi import Depends, Request
from app.repositories.items_repository import ItemsRepository
from app.services.items_service import ItemsService


def get_items_repo(request: Request) -> ItemsRepository:
    # Provided by app lifespan in main.py
    return request.app.state.items_repo  # type: ignore[attr-defined]


def get_items_service(
    repo: Annotated[ItemsRepository, Depends(get_items_repo)],
) -> ItemsService:
    return ItemsService(repo)
