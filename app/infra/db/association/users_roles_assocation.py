"""
Association table for many-to-many relationship between users and roles.
"""

from sqlalchemy import Column, ForeignKey, String, Table

from app.infra.db.orm import Base

# Association table for users and roles many-to-many relationship
UsersRolesAssociation = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("role_id", String, ForeignKey("roles.id"), primary_key=True),
)
