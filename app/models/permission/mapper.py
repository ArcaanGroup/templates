"""
Permission Mapper - handles conversion between PermissionDomain and Permission DTO
The Domain is the core of conversions
The Domain gets converted from DTO
And DTO gets converted from Domain
No Direct conversions from Entity to DTO or DTO to Entity (no entities needed for JSON repository)
"""

from app.models.permission.domain import PermissionDomain
from app.models.permission.dto import Permission as PermissionDTO


class PermissionMapper:
    """Mapper class to handle conversions between Permission representations."""

    @staticmethod
    def to_dto(domain_permission: PermissionDomain) -> PermissionDTO:
        """Convert domain Permission to DTO."""
        return PermissionDTO(
            id=domain_permission.id,
            title=domain_permission.title,
            description=domain_permission.description,
            policies=domain_permission.policies,
            created_at=domain_permission.created_at,
            updated_at=domain_permission.updated_at,
        )
