from typing import Annotated, List

from fastapi import APIRouter, Depends

from app.core.deps import get_items_service
from app.schemas.items_schema import ItemCreate, ItemOut, ItemUpdate
from app.services.items_service import ItemsService

router = APIRouter(prefix="/items", tags=["items"])

ServiceDep = Annotated[ItemsService, Depends(get_items_service)]


@router.get("/", response_model=List[ItemOut], summary="List items")
def list_items(service: ServiceDep):
    return service.list_items()


@router.post("/", response_model=ItemOut, status_code=201, summary="Create item")
def create_item(payload: ItemCreate, service: ServiceDep):
    return service.create_item(payload)


@router.get("/{item_id}", response_model=ItemOut, summary="Get item by ID")
def get_item(item_id: int, service: ServiceDep):
    return service.get_item(item_id)


@router.put("/{item_id}", response_model=ItemOut, summary="Replace item")
def replace_item(item_id: int, payload: ItemCreate, service: ServiceDep):
    return service.replace_item(item_id, payload)


@router.patch("/{item_id}", response_model=ItemOut, summary="Update item")
def update_item(item_id: int, payload: ItemUpdate, service: ServiceDep):
    return service.update_item(item_id, payload)


@router.delete("/{item_id}", status_code=204, summary="Delete item")
def delete_item(item_id: int, service: ServiceDep):
    service.delete_item(item_id)
    return None
