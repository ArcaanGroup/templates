"""In-memory cache implementation"""
import asyncio
from typing import Any

from app.application.interfaces.cache import CacheInterface


class MemoryCache(CacheInterface):
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                import time
                if time.time() < expiry:
                    return value
                else:
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL"""
        async with self._lock:
            import time
            expiry = time.time() + ttl
            self._cache[key] = (value, expiry)
    
    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        async with self._lock:
            if key in self._cache:
                import time
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return True
                else:
                    del self._cache[key]
            return False

