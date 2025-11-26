"""Role ORM model"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.infrastructure.database.base import Base

# Using a simple string column to store UUIDs for cross-database compatibility
# This works across SQLite, PostgreSQL, and other databases
ID_TYPE = String(36)  # Standard UUID string length


class RoleModel(Base):
    """Role SQLAlchemy model"""

    __tablename__ = "roles"

    id = Column(ID_TYPE, primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(50), nullable=False, unique=True)
    description = Column(String(250), nullable=True)
    # Store permissions as a JSON string to be compatible with both PostgreSQL and SQLite
    permissions = Column(String(1000), nullable=True, default="[]")  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Many-to-many relationship with users
    users = relationship("UserModel", secondary="user_roles", back_populates="roles")


# Association table for many-to-many relationship between users and roles
class UserRoleModel(Base):
    """Association table for many-to-many relationship between users and roles"""

    __tablename__ = "user_roles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(ID_TYPE, ForeignKey("roles.id"), primary_key=True)
