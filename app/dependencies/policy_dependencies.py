"""Policy-related dependencies and dependency injection logic."""

from fastapi import Depends

from app.interface.repositories.policy_repository_interface import (
    IPolicyRepository,
)
from app.repository.policy_repository import JSONPolicyRepository
from app.service.policy_service import PolicyService


async def get_policy_repository() -> IPolicyRepository:
    """Dependency to provide JSONPolicyRepository instance."""
    return JSONPolicyRepository()


async def get_policy_service(
    policy_repository: IPolicyRepository = Depends(get_policy_repository),
) -> PolicyService:
    """Dependency to provide PolicyService instance."""
    return PolicyService(policy_repository)
