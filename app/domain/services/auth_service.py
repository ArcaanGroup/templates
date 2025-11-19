"""Authentication domain services"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings
from app.domain.entities.user import User
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.value_objects.email import Email


class PasswordService:
    """Domain service for password-related operations"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        from passlib.context import CryptContext
        from passlib.exc import UnknownHashError

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError:
            # Return False if hash is invalid instead of raising an exception
            return False

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
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        import secrets

        jti = secrets.token_urlsafe(16)  # unique identifier for the token

        claims = {"sub": subject, "exp": expire, "type": "access", "jti": jti}
        encoded_jwt = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Create a refresh token as a signed JWT"""
        import secrets

        jti = secrets.token_urlsafe(32)  # unique identifier for the token
        return TokenService.create_refresh_token_with_jti(user_id, jti, expires_delta)

    @staticmethod
    def create_refresh_token_with_jti(
        user_id: int, jti: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token as a signed JWT with a specific jti"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )

        claims = {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": jti}
        encoded_jwt = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[str]:
        """Decode an access token and return the subject"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            subject: str = payload.get("sub")
            token_type: str = payload.get("type")

            if subject is None or token_type != "access":
                return None
            return subject
        except JWTError:
            return None

    @staticmethod
    def decode_refresh_token(token: str) -> Optional[str]:
        """Decode a refresh token and return the user_id (subject)"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            subject: str = payload.get("sub")
            token_type: str = payload.get("type")

            if subject is None or token_type != "refresh":
                return None
            return subject
        except JWTError:
            return None

    @staticmethod
    def create_refresh_token_entity(
        user_id: int, expires_delta: Optional[timedelta] = None
    ) -> RefreshToken:
        """Create a refresh token entity with proper expiration time"""
        if expires_delta:
            expires_at = datetime.now(timezone.utc) + expires_delta
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )

        import secrets

        token = secrets.token_urlsafe(32)

        return RefreshToken(token=token, user_id=user_id, expires_at=expires_at)


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

        if not user.verify_password(password):
            raise AuthenticationFailedException("Invalid credentials")

        return True
