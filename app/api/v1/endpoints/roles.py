"""Role management endpoints"""

from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_create_role_use_case,
    get_delete_role_use_case,
    get_get_role_use_case,
    get_list_roles_use_case,
    get_update_role_use_case,
    authorization_dependency,
)
from app.application.dto.role_dto import RoleCreateDTO, RoleDTO, RoleUpdateDTO
from app.application.use_cases.roles.create_role import CreateRoleUseCase
from app.application.use_cases.roles.delete_role import DeleteRoleUseCase
from app.application.use_cases.roles.get_role import GetRoleUseCase
from app.application.use_cases.roles.list_roles import ListRolesUseCase
from app.application.use_cases.roles.update_role import UpdateRoleUseCase
from app.schema.response import StandardResponse


router = APIRouter()


@router.post("/", response_model=StandardResponse[RoleDTO])
async def create_role(
    dto: RoleCreateDTO,
    _: dict = Depends(authorization_dependency(required=["role:write"])),
    use_case: CreateRoleUseCase = Depends(get_create_role_use_case),
) -> StandardResponse[RoleDTO]:
    """Create a new role"""
    try:
        role = await use_case.execute(dto)
        return StandardResponse[RoleDTO](
            success=True,
            message="Role created successfully",
            payload=role
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{role_id}", response_model=StandardResponse[RoleDTO])
async def get_role(
    role_id: uuid.UUID,
    use_case: GetRoleUseCase = Depends(get_get_role_use_case),
) -> StandardResponse[RoleDTO]:
    """Get a role by ID"""
    try:
        role = await use_case.execute(role_id)
        return StandardResponse[RoleDTO](
            success=True,
            message="Role retrieved successfully",
            payload=role
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/", response_model=StandardResponse[List[RoleDTO]])
async def list_roles(
    use_case: ListRolesUseCase = Depends(get_list_roles_use_case),
) -> StandardResponse[List[RoleDTO]]:
    """List all roles"""
    roles = await use_case.execute()
    return StandardResponse[List[RoleDTO]](
        success=True,
        message="Roles retrieved successfully",
        payload=roles
    )


@router.put("/{role_id}", response_model=StandardResponse[RoleDTO])
async def update_role(
    role_id: uuid.UUID,
    dto: RoleUpdateDTO,
    _: dict = Depends(authorization_dependency(required=["role:write"])),
    use_case: UpdateRoleUseCase = Depends(get_update_role_use_case),
) -> StandardResponse[RoleDTO]:
    """Update an existing role"""
    try:
        updated_role = await use_case.execute(role_id, dto)
        return StandardResponse[RoleDTO](
            success=True,
            message="Role updated successfully",
            payload=updated_role
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{role_id}", response_model=StandardResponse[bool])
async def delete_role(
    role_id: uuid.UUID,
    _: dict = Depends(authorization_dependency(required=["role:delete"])),
    use_case: DeleteRoleUseCase = Depends(get_delete_role_use_case),
) -> StandardResponse[bool]:
    """Delete a role by ID"""
    try:
        deleted = await use_case.execute(role_id)
        return StandardResponse[bool](
            success=True,
            message="Role deleted successfully",
            payload=deleted
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
