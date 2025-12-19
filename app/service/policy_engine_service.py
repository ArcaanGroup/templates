"""
Policy Engine Service - handles policy evaluation and validation.

This service implements a policy evaluation engine that validates policies
and can be extended with custom policy rules (time-based, resource-based, etc.).
"""

from typing import List, Optional

from app.error.exceptions import UnauthorizedException
from app.interface.repositories.policy_repository_interface import (
    IPolicyRepository,
)
from app.models.policy.domain import PolicyDomain


class PolicyEngineService:
    """
    Service for evaluating and validating policies.

    This engine validates that policies exist and can be extended
    to support more complex policy evaluation rules.
    """

    def __init__(self, policy_repository: IPolicyRepository):
        """
        Initialize the policy engine service.

        Args:
            policy_repository: Repository for accessing policy data
        """
        self.policy_repository = policy_repository

    async def evaluate_policies(
        self,
        policy_ids: List[str],
        context: Optional[dict] = None,
    ) -> None:
        """
        Evaluate a list of policies and raise an exception if any policy is invalid.

        This method validates that:
        1. All policy IDs exist in the repository
        2. All policies are active/valid (can be extended with custom rules)

        Args:
            policy_ids: List of policy IDs to evaluate
            context: Optional context dictionary for policy evaluation
                    (e.g., user info, resource info, time constraints)
                    Can be extended for future policy rules

        Raises:
            UnauthorizedException: If any policy is invalid or violated
        """
        if not policy_ids:
            # Empty policy list is valid (no policies to enforce)
            return

        # Validate that all policies exist
        invalid_policies = []
        policies: List[PolicyDomain] = []

        for policy_id in policy_ids:
            policy = await self.policy_repository.get_by_id(policy_id)
            if policy is None:
                invalid_policies.append(policy_id)
            else:
                policies.append(policy)

        # If any policies are invalid, raise an exception
        if invalid_policies:
            raise UnauthorizedException(
                message=f"Invalid or missing policies: {', '.join(invalid_policies)}",
                details={"invalid_policy_ids": invalid_policies},
            )

        # Evaluate each policy with custom rules
        # This is where you can add more complex policy evaluation logic
        for policy in policies:
            await self._evaluate_policy(policy, context)

    async def _evaluate_policy(
        self,
        policy: PolicyDomain,
        context: Optional[dict] = None,
    ) -> None:
        """
        Evaluate a single policy with custom rules.

        This method can be extended to implement:
        - Time-based policies (e.g., only allow access during business hours)
        - Resource-based policies (e.g., user can only access their own resources)
        - IP-based policies (e.g., only allow access from specific IP ranges)
        - Rate limiting policies
        - Custom business rules based on policy title/description

        Args:
            policy: The policy domain object to evaluate
            context: Optional context for policy evaluation

        Raises:
            UnauthorizedException: If the policy is violated
        """
        # Base validation: all policies pass by default
        # Extend this method to add custom policy evaluation logic

        # Example: You could check policy title for special handling
        # if policy.title == "time_restricted":
        #     await self._check_time_restriction(context)
        # elif policy.title == "resource_owner_only":
        #     await self._check_resource_ownership(policy, context)
