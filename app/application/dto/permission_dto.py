"""Permission DTOs"""
from typing import List
import uuid

from pydantic import BaseModel


class PermissionDTO(BaseModel):
    """DTO for permission data"""
    id: uuid.UUID
    title: str
    description: str
    policies: List[str]
