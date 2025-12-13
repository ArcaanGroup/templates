from datetime import datetime
from typing import List

from pydantic import BaseModel


class PermissionBase(BaseModel):
    """Base Permission model with common fields."""

    title: str
    description: str
    policies: List[str]  # List of policy IDs


class Permission(PermissionBase):
    """Public Permission model without sensitive data"""

    id: str
    created_at: datetime
    updated_at: datetime
