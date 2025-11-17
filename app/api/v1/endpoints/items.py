"""Item endpoints"""
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params

from app.api.dependencies import (
    get_create_item_use_case,
    get_delete_item_use_case,
    get_get_item_use_case,
    get_list_items_use_case,
    get_update_item_use_case,
)
from app.application.dto.item_dto import ItemCreateDTO, ItemDTO, ItemUpdateDTO
from app.application.use_cases.items.create_item import CreateItemUseCase
from app.application.use_cases.items.delete_item import DeleteItemUseCase
from app.application.use_cases.items.get_item import GetItemUseCase
from app.application.use_cases.items.list_items import ListItemsUseCase
from app.application.use_cases.items.update_item import UpdateItemUseCase
from app.core.exceptions import map_domain_exception_to_http
from app.domain.exceptions.item_exceptions import ItemNotFoundException
from app.schema.response import StandardResponse, success

router = APIRouter()


@router.post(
    "/",
    response_model=StandardResponse[ItemDTO],
    status_code=status.HTTP_201_CREATED
)
async def create_item(
    payload: ItemCreateDTO,
    use_case: CreateItemUseCase = Depends(get_create_item_use_case)
):
    """Create a new item"""
    try:
        result = await use_case.execute(payload)
        return success(result, message="Item created successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=StandardResponse[Page[ItemDTO]])
async def list_items(
    params: Params = Depends(),
    use_case: ListItemsUseCase = Depends(get_list_items_use_case)
):
    """List items with pagination"""
    result = await use_case.execute(params)
    return success(result, message="Items retrieved successfully")


@router.get("/{item_id}", response_model=StandardResponse[ItemDTO])
async def get_item(
    item_id: int,
    use_case: GetItemUseCase = Depends(get_get_item_use_case)
):
    """Get item by ID"""
    try:
        result = await use_case.execute(item_id)
        return success(result, message="Item retrieved successfully")
    except ItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.put("/{item_id}", response_model=StandardResponse[ItemDTO])
async def update_item(
    item_id: int,
    payload: ItemUpdateDTO,
    use_case: UpdateItemUseCase = Depends(get_update_item_use_case)
):
    """Update an item"""
    try:
        result = await use_case.execute(item_id, payload)
        return success(result, message="Item updated successfully")
    except ItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    use_case: DeleteItemUseCase = Depends(get_delete_item_use_case)
):
    """Delete an item"""
    try:
        await use_case.execute(item_id)
    except ItemNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

