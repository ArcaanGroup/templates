"""Item domain service"""
from app.domain.entities.item import Item


class ItemService:
    """Domain service for item-related business logic that doesn't belong to a single entity"""
    
    @staticmethod
    def calculate_discount_price(item: Item, discount_percentage: float) -> float:
        """Calculate discounted price"""
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100")
        
        discount = item.price * (discount_percentage / 100)
        return item.price - discount
    
    @staticmethod
    def is_expensive_item(item: Item, threshold: float = 1000.0) -> bool:
        """Check if item is expensive"""
        return item.price > threshold

