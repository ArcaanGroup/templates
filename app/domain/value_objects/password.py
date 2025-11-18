"""Password value object"""

from dataclasses import dataclass
from typing import Optional

from passlib.context import CryptContext

from app.domain.exceptions.auth_exceptions import InvalidPasswordException


@dataclass(frozen=True)
class Password:
    """Password value object with hashing and verification"""

    value: str
    hashed: Optional[str] = None

    def __post_init__(self):
        """Validate password after initialization"""
        if not self._is_valid_password(self.value):
            raise InvalidPasswordException("Password does not meet requirements")

        # If no hash is provided, hash the password
        if self.hashed is None:
            object.__setattr__(self, "hashed", self._hash_password(self.value))

    def _is_valid_password(self, password: str) -> bool:
        """Validate password strength"""
        # At least 8 characters, one uppercase, one lowercase, one digit
        if len(password) < 8:
            return False
        if not any(c.isupper() for c in password):
            return False
        if not any(c.islower() for c in password):
            return False
        if not any(c.isdigit() for c in password):
            return False
        return True

    def _hash_password(self, password: str) -> str:
        """Hash a plain password"""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def verify(self, plain_password: str) -> bool:
        """Verify if plain password matches the hash"""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, self.hashed)

    def __str__(self) -> str:
        """String representation (should not expose password)"""
        return "<hashed>"
