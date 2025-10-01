from typing import List

from fastapi import HTTPException, status

from app.repositories.items_repository import ItemsRepository
from app.schemas.items_schema import ItemCreate, ItemOut, ItemUpdate


class ItemsService:
    def __init__(self, repo: ItemsRepository):
        self.repo = repo

    def list_items(self) -> List[ItemOut]:
        return self.repo.list()

    def get_item(self, item_id: int) -> ItemOut:
        item = self.repo.get(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def create_item(self, payload: ItemCreate) -> ItemOut:
        # Example business rule: names must be unique (in-memory check)
        if any(i.name == payload.name for i in self.repo.list()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Item name already exists",
            )
        return self.repo.create(payload)

    def replace_item(self, item_id: int, payload: ItemCreate) -> ItemOut:
        item = self.repo.replace(item_id, payload)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def update_item(self, item_id: int, payload: ItemUpdate) -> ItemOut:
        item = self.repo.update(item_id, payload)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    def delete_item(self, item_id: int) -> None:
        ok = self.repo.delete(item_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Item not found")
