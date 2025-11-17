"""Cache interface"""
from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Cache interface for caching operations"""
    
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass

