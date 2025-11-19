"""Event bus interface"""
from abc import ABC, abstractmethod

from app.domain.events.base import DomainEvent


class EventBusInterface(ABC):
    """Event bus interface for publishing domain events"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: type[DomainEvent], handler: callable) -> None:
        """Subscribe to an event type"""
        pass

