"""Money value object"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    """Money value object - immutable and validated"""
    
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self) -> None:
        """Validate money"""
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
    
    def __add__(self, other: "Money") -> "Money":
        """Add two money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        """Subtract two money objects"""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, multiplier: Decimal | float | int) -> "Money":
        """Multiply money by a scalar"""
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

