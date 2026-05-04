"""
User-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dependencies.role_dependencies import get_role_repository
from app.application.use_cases.user_use_cases import UserUseCase
from app.infrastructure.core.database import get_db_session
from app.infrastructure.repositories.user_repository import UserRepository
from app.interface.repository.role_repository_interface import IRoleRepository
from app.interface.repository.user_repository_interface import IUserRepository


async def get_user_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    """Dependency to provide UserRepository instance with database session."""
    return UserRepository(db_session=db_session)


async def get_user_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> UserUseCase:
    """Dependency to provide UserUseCase instance with database session."""
    return UserUseCase(user_repository, role_repository)
