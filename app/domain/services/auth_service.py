"""Authentication domain services"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.domain.entities.user import User
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.value_objects.email import Email


class PasswordService:
    """Domain service for password-related operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain password"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)


class TokenService:
    """Domain service for token-related operations"""

    @staticmethod
    def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token with the specified subject"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        claims = {"sub": subject, "exp": expire}
        encoded_jwt = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        """Decode an access token and return the subject"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            subject: str = payload.get("sub")
            if subject is None:
                return None
            return subject
        except JWTError:
            return None


class UserService:
    """Domain service for user-related operations"""

    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        is_active: bool = True,
    ) -> User:
        """Create a new user with the provided details"""
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        from app.domain.value_objects.username import Username
        from app.domain.entities.user import User

        # Create value objects
        username_obj = Username(username)
        email_obj = Email(email)
        password_obj = Password(password)

        # Create and return the user
        return User(
            username=username_obj, email=email_obj, password=password_obj, is_active=is_active
        )

    @staticmethod
    def authenticate_user(user: User, password: str) -> bool:
        """Authenticate a user with the provided password"""
        if not user.is_active:
            raise AuthenticationFailedException("User account is deactivated")

        return user.verify_password(password)
