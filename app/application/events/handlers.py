"""Event handlers"""
from app.domain.events.item_created import ItemCreatedEvent


async def handle_item_created(event: ItemCreatedEvent) -> None:
    """Handle item created event"""
    # Example: Send notification, update cache, etc.
    print(f"Item created: {event.item_id} - {event.name}")

