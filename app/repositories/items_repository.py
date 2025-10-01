from __future__ import annotations

from typing import Optional, Protocol

from app.schemas.items_schema import ItemCreate, ItemOut, ItemUpdate


class ItemsRepository(Protocol):
    def list(self) -> list[ItemOut]: ...
    def get(self, item_id: int) -> Optional[ItemOut]: ...
    def create(self, payload: ItemCreate) -> ItemOut: ...
    def replace(self, item_id: int, payload: ItemCreate) -> Optional[ItemOut]: ...
    def update(self, item_id: int, payload: ItemUpdate) -> Optional[ItemOut]: ...
    def delete(self, item_id: int) -> bool: ...


class InMemoryItemsRepository:
    def __init__(self) -> None:
        self._db: dict[int, ItemOut] = {}
        self._next_id = 1

    def _next(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def list(self) -> list[ItemOut]:
        return list(self._db.values())

    def get(self, item_id: int) -> Optional[ItemOut]:
        return self._db.get(item_id)

    def create(self, payload: ItemCreate) -> ItemOut:
        item = ItemOut(id=self._next(), **payload.model_dump())
        self._db[item.id] = item
        return item

    def replace(self, item_id: int, payload: ItemCreate) -> Optional[ItemOut]:
        if item_id not in self._db:
            return None
        item = ItemOut(id=item_id, **payload.model_dump())
        self._db[item_id] = item
        return item

    def update(self, item_id: int, payload: ItemUpdate) -> Optional[ItemOut]:
        existing = self._db.get(item_id)
        if not existing:
            return None
        data = existing.model_dump()
        data.update(payload.model_dump(exclude_unset=True))
        item = ItemOut(**data)
        self._db[item_id] = item
        return item

    def delete(self, item_id: int) -> bool:
        if item_id in self._db:
            del self._db[item_id]
            return True
        return False
