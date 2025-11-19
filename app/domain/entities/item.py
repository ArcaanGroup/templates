"""Item domain entity"""
from datetime import datetime

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.item_exceptions import InvalidItemPriceException, ItemNameRequiredException


class Item(BaseEntity):
    """Item domain entity with business logic"""
    
    def __init__(
        self,
        name: str,
        price: float,
        is_offer: bool = False,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        super().__init__(id, created_at, updated_at)
        self._validate_name(name)
        self._validate_price(price)
        
        self._name = name
        self._price = price
        self._is_offer = is_offer
    
    @property
    def name(self) -> str:
        """Item name"""
        return self._name
    
    @property
    def price(self) -> float:
        """Item price"""
        return self._price
    
    @property
    def is_offer(self) -> bool:
        """Whether item is on offer"""
        return self._is_offer
    
    def update_price(self, new_price: float) -> None:
        """Update item price with validation"""
        self._validate_price(new_price)
        self._price = new_price
        self.mark_as_updated()
    
    def update_name(self, new_name: str) -> None:
        """Update item name with validation"""
        self._validate_name(new_name)
        self._name = new_name
        self.mark_as_updated()
    
    def set_offer(self, is_offer: bool) -> None:
        """Set offer status"""
        self._is_offer = is_offer
        self.mark_as_updated()
    
    def _validate_name(self, name: str) -> None:
        """Validate item name"""
        if not name or not name.strip():
            raise ItemNameRequiredException()
        if len(name) > 255:
            raise ValueError("Item name cannot exceed 255 characters")
    
    def _validate_price(self, price: float) -> None:
        """Validate item price"""
        if price < 0:
            raise InvalidItemPriceException(price)
        if price > 1_000_000:
            raise InvalidItemPriceException(price)

