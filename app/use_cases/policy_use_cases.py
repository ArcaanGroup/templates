from typing import List

from app.interface.repositories.policy_repository_interface import IPolicyRepository
from app.models.policy.domain import PolicyDomain


class PolicyUseCase:
    """Use case layer for policy operations."""

    def __init__(self, policy_repository: IPolicyRepository):
        self.policy_repository = policy_repository

    async def get_all_policies(self) -> List[PolicyDomain]:
        return await self.policy_repository.get_all()

    async def get_policy_by_id(self, policy_id: str) -> PolicyDomain:
        policy = await self.policy_repository.get_by_id(policy_id)
        if policy is None:
            raise ValueError(f"Policy with ID {policy_id} not found")
        return policy

    async def get_policy_by_title(self, title: str) -> PolicyDomain:
        policy = await self.policy_repository.get_by_title(title)
        if policy is None:
            raise ValueError(f"Policy with title {title} not found")
        return policy

    async def search_policies_by_title(self, title_query: str) -> List[PolicyDomain]:
        return await self.policy_repository.search_by_title(title_query)
