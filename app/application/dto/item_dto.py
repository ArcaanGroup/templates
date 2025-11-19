"""Item DTOs"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ItemCreateDTO(BaseModel):
    """DTO for creating an item"""

    name: str
    price: float
    is_offer: bool = False


class ItemUpdateDTO(BaseModel):
    """DTO for updating an item"""

    name: str | None = None
    price: float | None = None
    is_offer: bool | None = None


class ItemDTO(BaseModel):
    """DTO for item response"""

    id: int
    name: str
    price: float
    is_offer: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
