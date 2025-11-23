"""Item created domain event"""
from dataclasses import dataclass
from app.domain.events.base import DomainEvent


@dataclass(frozen=True)
class ItemCreatedEvent(DomainEvent):
    """Event raised when an item is created"""

    item_id: int
    name: str
    price: float
