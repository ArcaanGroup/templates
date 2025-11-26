"""Title value object"""

from dataclasses import dataclass
from typing import Any

from app.domain.exceptions.auth_exceptions import InvalidUsernameException


@dataclass(frozen=True)
class Title:
    """Title value object representing a title with validation"""

    value: str

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise InvalidUsernameException("Title must be a non-empty string")
        if len(self.value.strip()) < 1:
            raise InvalidUsernameException("Title must be at least 1 character long")
        if len(self.value.strip()) > 100:  # Reasonable max length
            raise InvalidUsernameException("Title must be no more than 100 characters long")

    def __str__(self) -> str:
        return self.value

    @classmethod
    def create(cls, value: str) -> "Title":
        """Create a Title instance with validation"""
        return cls(value)
