"""User created domain event"""

from dataclasses import dataclass
from datetime import datetime

from app.domain.events.base import DomainEvent


@dataclass(frozen=True)
class UserCreatedEvent(DomainEvent):
    """Event raised when a user is created"""

    user_id: int
    username: str
    email: str
    created_at: datetime
