from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.dependencies.auth_dependencies import get_authorized_user
from app.dependencies.user_dependencies import get_user_service
from app.models import User, UserCreate, UserUpdate
from app.models.responses import StandardResponse, success
from app.use_cases.user_use_cases import UserUseCase
from app.utils.auth.permission import Permission

# Create router with prefix and tags
user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/", response_model=StandardResponse[Page[User]])
async def get_users(
    service: UserUseCase = Depends(get_user_service),
    params: Params = Depends(),
    _=Depends(get_authorized_user([Permission.Users_Read])),
):
    """Get a list of all users"""
    users = await service.get_all(params)

    return success(
        message="Users retrieved successfully",
        payload=users,
    )


@user_router.post("/", response_model=StandardResponse[User])
async def create_user(
    user_create: UserCreate,
    service: UserUseCase = Depends(get_user_service),
    _=Depends(get_authorized_user([Permission.Users_Create])),
):
    """Create a new user"""
    user = await service.create(user_create)

    return success(message="User created successfully", payload=user)


@user_router.get("/{user_id}", response_model=StandardResponse[User])
async def get_user(
    user_id: str,
    service: UserUseCase = Depends(get_user_service),
    _=Depends(get_authorized_user([Permission.Users_Read])),
):
    """Get a specific user by ID"""
    user = await service.get_by_id(user_id)

    return success(message="User retrieved successfully", payload=user)


@user_router.put("/{user_id}", response_model=StandardResponse[User])
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    service: UserUseCase = Depends(get_user_service),
    _=Depends(get_authorized_user([Permission.Users_Update])),
):
    """Update a specific user by ID"""
    user = await service.update(user_id, user_update)

    return success(message="User updated successfully", payload=user)


@user_router.delete("/{user_id}", response_model=StandardResponse[User])
async def delete_user(
    user_id: str,
    service: UserUseCase = Depends(
        get_user_service,
    ),
    _=Depends(get_authorized_user([Permission.Users_Delete])),
):
    """Delete a specific user by ID"""
    deleted_user = await service.delete(user_id)

    return success(message="User deleted successfully", payload=deleted_user)


@user_router.post("/{user_id}/roles/{role_id}", response_model=StandardResponse[User])
async def assign_role_to_user(
    user_id: str,
    role_id: str,
    service: UserUseCase = Depends(get_user_service),
    _=Depends(get_authorized_user([Permission.Users_AssignRole])),
):
    """Assign a role to a user"""
    user = await service.assign_role(user_id, role_id)

    return success(message="Role assigned to user successfully", payload=user)


@user_router.delete("/{user_id}/roles/{role_id}", response_model=StandardResponse[User])
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    service: UserUseCase = Depends(get_user_service),
    _=Depends(get_authorized_user([Permission.Users_UnassignRole])),
):
    """Remove a role from a user"""
    user = await service.remove_role(user_id, role_id)

    return success(message="Role removed from user successfully", payload=user)
