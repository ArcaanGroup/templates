"""
True Clean Architecture Use Cases for Policy operations.
Use cases contain business logic and are independent of frameworks and external concerns.
"""

from dataclasses import dataclass
from typing import List, Optional

from app.domain.entities import PolicyEntity
from app.interface.repository.policy_repository_interface import IPolicyRepository


@dataclass(frozen=True)
class GetAllPoliciesRequest:
    """Input port for getting all policies."""
    pass


@dataclass(frozen=True)
class GetAllPoliciesResponse:
    """Output port for getting all policies."""
    policies: List[PolicyEntity]


@dataclass(frozen=True)
class GetPolicyByIdRequest:
    """Input port for getting a policy by ID."""
    policy_id: str


@dataclass(frozen=True)
class GetPolicyByIdResponse:
    """Output port for getting a policy by ID."""
    policy: PolicyEntity


@dataclass(frozen=True)
class GetPolicyByTitleRequest:
    """Input port for getting a policy by title."""
    title: str


@dataclass(frozen=True)
class GetPolicyByTitleResponse:
    """Output port for getting a policy by title."""
    policy: PolicyEntity


@dataclass(frozen=True)
class SearchPoliciesRequest:
    """Input port for searching policies by title."""
    title_query: str


@dataclass(frozen=True)
class SearchPoliciesResponse:
    """Output port for searching policies by title."""
    policies: List[PolicyEntity]


class GetAllPoliciesUseCase:
    """Use case for retrieving all policies."""

    def __init__(self, policy_repository: IPolicyRepository):
        self._policy_repo = policy_repository

    async def execute(self, request: GetAllPoliciesRequest) -> GetAllPoliciesResponse:
        """Execute the use case to get all policies."""
        policies = await self._policy_repo.get_all()
        return GetAllPoliciesResponse(policies=policies)


class GetPolicyByIdUseCase:
    """Use case for retrieving a policy by ID."""

    def __init__(self, policy_repository: IPolicyRepository):
        self._policy_repo = policy_repository

    async def execute(
        self, request: GetPolicyByIdRequest
    ) -> GetPolicyByIdResponse:
        """Execute the use case to get a policy by ID."""
        policy = await self._policy_repo.get_by_id(request.policy_id)
        if policy is None:
            raise ValueError(f"Policy with ID {request.policy_id} not found")
        return GetPolicyByIdResponse(policy=policy)


class GetPolicyByTitleUseCase:
    """Use case for retrieving a policy by title."""

    def __init__(self, policy_repository: IPolicyRepository):
        self._policy_repo = policy_repository

    async def execute(
        self, request: GetPolicyByTitleRequest
    ) -> GetPolicyByTitleResponse:
        """Execute the use case to get a policy by title."""
        policy = await self._policy_repo.get_by_title(request.title)
        if policy is None:
            raise ValueError(f"Policy with title {request.title} not found")
        return GetPolicyByTitleResponse(policy=policy)


class SearchPoliciesUseCase:
    """Use case for searching policies by title."""

    def __init__(self, policy_repository: IPolicyRepository):
        self._policy_repo = policy_repository

    async def execute(
        self, request: SearchPoliciesRequest
    ) -> SearchPoliciesResponse:
        """Execute the use case to search policies by title."""
        policies = await self._policy_repo.search_by_title(request.title_query)
        return SearchPoliciesResponse(policies=policies)
