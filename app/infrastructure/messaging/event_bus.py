"""Event bus implementation"""
from collections import defaultdict
from typing import Callable

from app.application.interfaces.event_bus import EventBusInterface
from app.domain.events.base import DomainEvent


class InMemoryEventBus(EventBusInterface):
    """In-memory event bus implementation"""
    
    def __init__(self):
        self._handlers: dict[type[DomainEvent], list[Callable]] = defaultdict(list)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event"""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            await handler(event)
    
    async def subscribe(self, event_type: type[DomainEvent], handler: Callable) -> None:
        """Subscribe to an event type"""
        self._handlers[event_type].append(handler)

