"""Base domain event"""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Base class for all domain events"""
    
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self) -> None:
        """Ensure event is immutable"""
        object.__setattr__(self, 'event_id', self.event_id)
        object.__setattr__(self, 'occurred_at', self.occurred_at)

