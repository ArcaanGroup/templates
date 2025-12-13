"""
Domain Entity for Permission - contains business logic and behavior
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4


@dataclass
class PermissionDomain:
    """Domain entity for Permission with business logic."""

    id: str
    title: str
    description: str
    policies: List[str]  # List of policy IDs
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        policies: List[str],
        permission_id: Optional[str] = None,
    ) -> "PermissionDomain":
        """Create a new PermissionDomain entity."""
        permission_id = permission_id or str(uuid4())
        now = datetime.now()

        return cls(
            id=permission_id,
            title=title,
            description=description,
            policies=policies,
            created_at=now,
            updated_at=now,
        )
