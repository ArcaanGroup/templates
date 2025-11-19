"""Item domain exceptions"""
from app.domain.exceptions.base import DomainException


class ItemNotFoundException(DomainException):
    """Raised when item is not found"""
    
    def __init__(self, item_id: int):
        super().__init__(f"Item with id {item_id} not found", {"item_id": item_id})


class InvalidItemPriceException(DomainException):
    """Raised when item price is invalid"""
    
    def __init__(self, price: float):
        super().__init__(f"Invalid item price: {price}", {"price": price})


class ItemNameRequiredException(DomainException):
    """Raised when item name is missing"""
    
    def __init__(self):
        super().__init__("Item name is required")

