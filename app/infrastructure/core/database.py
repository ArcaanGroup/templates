"""
Database engine and session setup using SQLAlchemy.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.core.config import Config

# Global variables to store engine and sessionmaker
_engine: Optional[AsyncEngine] = None
_async_sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """Get the async engine, initializing only when first needed."""
    global _engine
    if _engine is None:
        config = Config()
        _engine = create_async_engine(
            config.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,  # Verify connections before use
            pool_size=10,  # Number of connection pool
            max_overflow=20,  # Additional connections beyond pool_size
        )
    return _engine


def get_async_session_local() -> async_sessionmaker[AsyncSession]:
    """
    Get the async session maker, initializing engine and sessionmaker only when needed.

    Returns:
        An async sessionmaker instance for creating database sessions.
    """
    global _async_sessionmaker
    if _async_sessionmaker is None:
        engine = get_engine()  # This will initialize the engine if needed
        _async_sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return _async_sessionmaker


# For backward compatibility with existing code
def AsyncSessionLocal():
    """Alias for get_async_session_local() for backward compatibility."""
    sessionmaker = get_async_session_local()
    return sessionmaker()


async def get_db_session():
    """Dependency to provide database session."""
    async with get_async_session_local()() as session:
        yield session
