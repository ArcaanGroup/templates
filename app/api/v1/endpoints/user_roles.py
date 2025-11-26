"""User Role endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import (
    get_assign_role_to_user_use_case,
    get_get_user_roles_use_case,
)
from app.application.dto.user_role_dto import UserRoleAssignmentDTO, UserWithRolesDTO
from app.application.use_cases.user_roles.assign_role_to_user import AssignRoleToUserUseCase
from app.application.use_cases.user_roles.get_user_roles import GetUserRolesUseCase
from app.domain.exceptions.user_exceptions import UserNotFoundException
from app.domain.exceptions.role_exceptions import RoleNotFoundException
from app.schema.response import StandardResponse, success

router = APIRouter()


@router.post(
    "/{user_id}/roles",
    response_model=StandardResponse[UserWithRolesDTO],
    status_code=status.HTTP_201_CREATED
)
async def assign_roles_to_user(
    user_id: int,
    payload: UserRoleAssignmentDTO,
    use_case: AssignRoleToUserUseCase = Depends(get_assign_role_to_user_use_case)
):
    """Assign roles to a user"""
    try:
        # Override the user_id from the path to ensure consistency
        payload.user_id = user_id
        result = await use_case.execute(payload)
        # Convert the result to the expected DTO format
        role_titles = [role.title.value for role in result.roles]
        user_with_roles = UserWithRolesDTO(
            id=result.id,
            username=result.username.value,
            email=result.email.value,
            is_active=result.is_active,
            roles=role_titles
        )
        return success(user_with_roles, message="Roles assigned successfully")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RoleNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{user_id}/roles",
    response_model=StandardResponse[UserWithRolesDTO]
)
async def get_user_roles(
    user_id: int,
    use_case: GetUserRolesUseCase = Depends(get_get_user_roles_use_case)
):
    """Get roles assigned to a user"""
    try:
        result = await use_case.execute(user_id)
        return success(result, message="User roles retrieved successfully")
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
