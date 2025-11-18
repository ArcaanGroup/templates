"""Username value object"""

import re
from dataclasses import dataclass

from app.domain.exceptions.auth_exceptions import InvalidUsernameException


@dataclass(frozen=True)
class Username:
    """Username value object with validation"""

    value: str

    def __post_init__(self):
        """Validate username format after initialization"""
        if not self._is_valid_username(self.value):
            raise InvalidUsernameException(self.value)

    def _is_valid_username(self, username: str) -> bool:
        """Validate username format using regex"""
        # Username must be 3-20 characters, alphanumeric and underscores only
        pattern = r"^[a-zA-Z0-9_]{3,20}$"
        return re.match(pattern, username) is not None

    def __str__(self) -> str:
        """String representation of username"""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Compare usernames (case-insensitive)"""
        if isinstance(other, Username):
            return self.value.lower() == other.value.lower()
        return False

    def __hash__(self) -> int:
        """Hash based on lowercase username value"""
        return hash(self.value.lower())
