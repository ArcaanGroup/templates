"""
Role entity as SQLAlchemy ORM model.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user.entity import UserEntity


class RoleEntity(Base):
    """Role entity for database storage."""

    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Store permission IDs as JSON array to represent M:N relationship with permissions (JSON file based)

    # Use JSON for maximum compatibility across database backends
    # This ensures tests work with SQLite while maintaining functionality
    permission_ids: Mapped[list] = mapped_column(
        JSON, default=list, server_default="[]", nullable=False
    )

    # Relationship with users (many-to-many)
    users: Mapped[list["UserEntity"]] = relationship(
        "UserEntity", secondary="user_roles", back_populates="roles"
    )
