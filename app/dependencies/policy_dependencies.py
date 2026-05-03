"""Policy-related dependencies and dependency injection logic."""

from fastapi import Depends

from app.interface.repositories.policy_repository_interface import (
    IPolicyRepository,
)
from app.repository.policy_repository import JSONPolicyRepository
from app.use_cases.policy_engine_use_cases import PolicyEngineUseCase
from app.use_cases.policy_use_cases import PolicyUseCase


async def get_policy_repository() -> IPolicyRepository:
    """Dependency to provide JSONPolicyRepository instance."""
    return JSONPolicyRepository()


async def get_policy_service(
    policy_repository: IPolicyRepository = Depends(get_policy_repository),
) -> PolicyUseCase:
    """Dependency to provide PolicyUseCase instance."""
    return PolicyUseCase(policy_repository)


async def get_policy_engine_service(
    policy_repository: IPolicyRepository = Depends(get_policy_repository),
) -> PolicyEngineUseCase:
    """Dependency to provide PolicyEngineUseCase instance."""
    return PolicyEngineUseCase(policy_repository)
