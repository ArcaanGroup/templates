"""Item ORM model"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.infrastructure.database.base import Base


class ItemModel(Base):
    """Item SQLAlchemy model"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=False)
    is_offer = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

