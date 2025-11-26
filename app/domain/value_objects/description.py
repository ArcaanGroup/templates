"""Description value object"""

from dataclasses import dataclass
from typing import Any, Optional

from app.domain.exceptions.auth_exceptions import InvalidUsernameException


@dataclass(frozen=True)
class Description:
    """Description value object representing a description with validation"""

    value: Optional[str]

    def __post_init__(self):
        if self.value is not None:
            if not isinstance(self.value, str):
                raise InvalidUsernameException("Description must be a string if provided")
            if len(self.value.strip()) > 500:  # Reasonable max length
                raise InvalidUsernameException("Description must be no more than 500 characters long")

    def __str__(self) -> str:
        return self.value if self.value is not None else ""

    @classmethod
    def create(cls, value: Optional[str]) -> "Description":
        """Create a Description instance with validation"""
        return cls(value)
