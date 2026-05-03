"""
Shared SQLAlchemy base for all entities to ensure they're in the same registry.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
