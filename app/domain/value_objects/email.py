"""Email value object"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Email value object - immutable and validated"""
    
    value: str
    
    def __post_init__(self) -> None:
        """Validate email format"""
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value

