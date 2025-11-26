"""Permissions endpoints"""

from typing import List

from fastapi import APIRouter, Depends

from app.application.dto.permission_dto import PermissionDTO
from app.domain.services.permission_service import PermissionService
from app.schema.response import StandardResponse


router = APIRouter()


@router.get("/", response_model=StandardResponse[List[PermissionDTO]])
async def get_permissions() -> StandardResponse[List[PermissionDTO]]:
    """Get all available permissions"""
    permissions = PermissionService.get_permissions()
    return StandardResponse[List[PermissionDTO]](
        success=True,
        message="Permissions retrieved successfully",
        payload=permissions
    )
