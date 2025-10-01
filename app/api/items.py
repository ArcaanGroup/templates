from fastapi import APIRouter, HTTPException, status
from app.schemas import ItemCreate, ItemUpdate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])

# super-tiny in-memory store
_db: dict[int, ItemOut] = {}
_next_id = 1


def _get_next_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid


@router.get("/", response_model=list[ItemOut], summary="List items")
def list_items() -> list[ItemOut]:
    return list(_db.values())


@router.get("/{item_id}", response_model=ItemOut, summary="List items")
def get_item(item_id: int) -> ItemOut:
    item = _db.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return item


@router.post(
    "/",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create new item",
)
def create_item(payload: ItemCreate) -> ItemOut:
    item = ItemOut(id=_get_next_id(), **payload.model_dump())
    _db[item.id] = item
    return item


@router.put("/{item_id}", response_model=ItemOut, summary="Replace item")
def update_item(item_id: int, payload: ItemUpdate) -> ItemOut:
    existing = _db[item_id]
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    data = existing.model_dump()
    updates = payload.model_dump(exclude_unset=True)
    data.update(updates)
    item = ItemOut(**data)
    _db[item_id] = item
    return item


@router.delete(
    "/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete item"
)
def delete_item(item_id: int) -> None:
    if item_id not in _db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    del _db[item_id]
    return None
