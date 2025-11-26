"""Role DTOs"""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class RoleDTO(BaseModel):
    """DTO for role response"""
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    permissions: List[uuid.UUID] = []
    created_at: datetime
    updated_at: datetime


class RoleCreateDTO(BaseModel):
    """DTO for creating a role"""
    title: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    permissions: List[uuid.UUID] = []


class RoleUpdateDTO(BaseModel):
    """DTO for updating a role"""
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=250)
    permissions: Optional[List[uuid.UUID]] = None
