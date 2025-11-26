"""User Role DTOs"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class UserRoleAssignmentDTO(BaseModel):
    """DTO for assigning roles to a user"""

    user_id: int
    role_ids: List[UUID] = Field(..., description="List of role IDs to assign to the user")


class UserWithRolesDTO(BaseModel):
    """DTO for user with roles information"""

    id: int
    username: str
    email: str
    is_active: bool
    roles: List[str] = Field(default_factory=list, description="List of role titles")
