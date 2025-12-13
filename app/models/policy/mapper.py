"""
Policy Mapper - handles conversion between PolicyDomain and Policy DTO
The Domain is the core of conversions
The Domain gets converted from DTO
And DTO gets converted from Domain
No Direct conversions from Entity to DTO or DTO to Entity (no entities needed for JSON repository)
"""

from app.models.policy.domain import PolicyDomain
from app.models.policy.dto import Policy as PolicyDTO


class PolicyMapper:
    """Mapper class to handle conversions between Policy representations."""

    @staticmethod
    def to_dto(domain_policy: PolicyDomain) -> PolicyDTO:
        """Convert domain Policy to DTO."""
        return PolicyDTO(
            id=domain_policy.id,
            title=domain_policy.title,
            description=domain_policy.description,
            created_at=domain_policy.created_at,
            updated_at=domain_policy.updated_at,
        )
