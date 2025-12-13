"""
User-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.role_dependencies import get_role_repository
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService


async def get_user_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    """Dependency to provide UserRepository instance with database session."""
    return UserRepository(db_session=db_session)


async def get_user_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
):
    """Dependency to provide UserService instance with database session."""
    return UserService(user_repository, role_repository)
