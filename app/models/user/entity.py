"""
User entity as SQLAlchemy ORM model.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.refresh_token.entity import RefreshTokenEntity
    from app.models.role.entity import RoleEntity


class UserEntity(Base):
    """User entity for database storage."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship with refresh tokens
    refresh_tokens: Mapped[list["RefreshTokenEntity"]] = relationship(
        "RefreshTokenEntity", back_populates="user", cascade="all, delete-orphan"
    )

    # Relationship with roles (many-to-many)
    roles: Mapped[list["RoleEntity"]] = relationship(
        "RoleEntity", secondary="user_roles", back_populates="users"
    )
