"""Interface for policy repository operations."""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.policy.domain import PolicyDomain


class IPolicyRepository(ABC):
    """Interface for policy repository operations."""

    @abstractmethod
    async def get_by_id(self, policy_id: str) -> Optional[PolicyDomain]:
        """Get a policy by ID from the repository."""

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[PolicyDomain]:
        """Get a policy by title from the repository."""

    @abstractmethod
    async def get_all(self) -> List[PolicyDomain]:
        """Get all policies from the repository."""

    @abstractmethod
    async def search_by_title(self, title_query: str) -> List[PolicyDomain]:
        """Search policies by title from the repository."""
