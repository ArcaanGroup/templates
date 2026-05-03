from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.application.use_cases.role_use_cases import RoleUseCase
from app.infrastructure.dependencies.auth_dependencies import get_authorized_user
from app.infrastructure.dependencies.role_dependencies import get_role_service
from app.infrastructure.utils.auth.permission import Permission
from app.interface.dto import Role, RoleCreate, RoleUpdate
from app.interface.dto.responses import StandardResponse, success

# Create router with prefix and tags
role_router = APIRouter(prefix="/roles", tags=["roles"])


@role_router.get("/", response_model=StandardResponse[Page[Role]])
async def get_roles(
    params: Params = Depends(),
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_Read])),
):
    """Get a list of all roles"""
    roles = await service.get_all(params)
    return success(
        message="Roles retrieved successfully",
        payload=roles,
    )


@role_router.get("/{role_id}", response_model=StandardResponse[Role])
async def get_role_by_id(
    role_id: str,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_Read])),
):
    """Get a specific role by ID"""
    role = await service.get_by_id(role_id)
    return success(message="Role retrieved successfully", payload=role)


@role_router.post("/", response_model=StandardResponse[Role])
async def create_role(
    role_create: RoleCreate,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_Create])),
):
    """Create a new role"""
    role = await service.create(role_create)
    return success(message="Role created successfully", payload=role)


@role_router.put("/{role_id}", response_model=StandardResponse[Role])
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_Update])),
):
    """Update a specific role by ID"""
    role = await service.update(role_id, role_update)
    return success(message="Role updated successfully", payload=role)


@role_router.delete("/{role_id}", response_model=StandardResponse[Role])
async def delete_role(
    role_id: str,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_Delete])),
):
    """Delete a specific role by ID"""
    deleted_role = await service.delete(role_id)
    return success(message="Role deleted successfully", payload=deleted_role)


@role_router.post(
    "/{role_id}/permissions/{permission_id}", response_model=StandardResponse[Role]
)
async def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_AssignPermission])),
):
    """Assign a permission to a role"""
    role = await service.assign_permission_to_role(role_id, permission_id)
    return success(message="Permission assigned to role successfully", payload=role)


@role_router.delete(
    "/{role_id}/permissions/{permission_id}", response_model=StandardResponse[Role]
)
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    service: RoleUseCase = Depends(get_role_service),
    _=Depends(get_authorized_user([Permission.Roles_UnassignPermission])),
):
    """Remove a permission from a role"""
    role = await service.remove_permission_from_role(role_id, permission_id)
    return success(message="Permission removed from role successfully", payload=role)
