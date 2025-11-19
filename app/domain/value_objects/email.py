"""Email value object"""

import re
from dataclasses import dataclass
from typing import Union

from app.domain.exceptions.auth_exceptions import InvalidEmailException


@dataclass(frozen=True)
class Email:
    """Email value object with validation"""

    value: str

    def __post_init__(self):
        """Validate email format after initialization"""
        if not self._is_valid_email(self.value):
            raise InvalidEmailException(self.value)

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def __str__(self) -> str:
        """String representation of email"""
        return self.value

    def __eq__(self, other: Union["Email", object]) -> bool:
        """Compare emails (case-insensitive)"""
        if isinstance(other, Email):
            return self.value.lower() == other.value.lower()
        return False

    def __hash__(self) -> int:
        """Hash based on lowercase email value"""
        return hash(self.value.lower())
