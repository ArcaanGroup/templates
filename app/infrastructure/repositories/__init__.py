"""
Package containing repository implementations.
"""

from app.interface.repository.user_repository_interface import IUserRepository

from .user_repository import UserRepository

__all__ = ["UserRepository", "IUserRepository"]
