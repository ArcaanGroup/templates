from typing import List, Optional

from app.domain.entities import PolicyEntity
from app.infrastructure.error.exceptions import UnauthorizedException
from app.interface.repository.policy_repository_interface import IPolicyRepository


class PolicyEngineUseCase:
    """Use case layer for policy evaluation and validation."""

    def __init__(self, policy_repository: IPolicyRepository):
        self.policy_repository = policy_repository

    async def evaluate_policies(
        self,
        policy_ids: List[str],
        context: Optional[dict] = None,
    ) -> None:
        if not policy_ids:
            return

        invalid_policy_ids = []
        policies: List[PolicyEntity] = []

        for policy_id in policy_ids:
            policy = await self.policy_repository.get_by_id(policy_id)
            if policy is None:
                invalid_policy_ids.append(policy_id)
            else:
                policies.append(policy)

        if invalid_policy_ids:
            raise UnauthorizedException(
                message=f"Invalid or missing policies: {', '.join(invalid_policy_ids)}",
                details={"invalid_policy_ids": invalid_policy_ids},
            )

        for policy in policies:
            await self._evaluate_policy(policy, context)

    async def _evaluate_policy(
        self,
        policy: PolicyEntity,
        context: Optional[dict] = None,
    ) -> None:
        # Extend this method to implement custom policy evaluation logic.
        return
