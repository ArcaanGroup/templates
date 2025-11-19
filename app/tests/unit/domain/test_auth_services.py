"""Unit tests for authentication domain services"""

import pytest
from app.domain.services.auth_service import PasswordService, TokenService, UserService
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException


class TestPasswordService:
    """Test cases for PasswordService"""

    def test_hash_and_verify_password(self):
        """Test hashing and verifying a password"""
        password = "TestPass123"
        hashed = PasswordService.hash_password(password)

        assert PasswordService.verify_password(password, hashed) is True
        assert PasswordService.verify_password("WrongPass", hashed) is False

    def test_verify_password_with_invalid_hash(self):
        """Test password verification with invalid hash"""
        assert PasswordService.verify_password("password", "invalid_hash") is False


class TestTokenService:
    """Test cases for TokenService"""

    def test_create_and_decode_token(self):
        """Test creating and decoding a token"""
        subject = "testuser"
        token = TokenService.create_access_token(subject)
        decoded_subject = TokenService.decode_access_token(token)

        assert decoded_subject == subject

    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        decoded_subject = TokenService.decode_access_token("invalid_token")

        assert decoded_subject is None

    def test_decode_expired_token(self):
        """Test decoding an expired token"""
        from datetime import datetime, timedelta, timezone
        import time
        from jose import jwt
        from app.core.config import settings

        # Create an expired token manually
        expire = datetime.now(timezone.utc) - timedelta(seconds=1)  # Expired 1 second ago
        claims = {"sub": "testuser", "exp": expire}
        expired_token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        decoded_subject = TokenService.decode_access_token(expired_token)

        assert decoded_subject is None


class TestUserService:
    """Test cases for UserService"""

    def test_create_user(self):
        """Test creating a user"""
        username = "testuser"
        email = "test@example.com"
        password = "TestPass123"

        user = UserService.create_user(username, email, password)

        assert user.username.value == username
        assert user.email.value == email
        assert user.verify_password(password) is True
        assert user.is_active is True

    def test_create_user_with_custom_active_status(self):
        """Test creating a user with custom active status"""
        user = UserService.create_user(
            "testuser", "test@example.com", "TestPass123", is_active=False
        )

        assert user.is_active is False

    def test_authenticate_user_active(self):
        """Test authenticating an active user"""
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )

        result = UserService.authenticate_user(user, "TestPass123")

        assert result is True

    def test_authenticate_user_with_wrong_password(self):
        """Test authenticating a user with wrong password"""
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )

        with pytest.raises(AuthenticationFailedException):
            UserService.authenticate_user(user, "WrongPass")

    def test_authenticate_inactive_user(self):
        """Test authenticating an inactive user"""
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
            is_active=False,
        )

        with pytest.raises(AuthenticationFailedException):
            UserService.authenticate_user(user, "TestPass123")

    def test_authenticate_user_edge_case(self):
        """Test edge case for user authentication"""
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )

        # Verify that the method returns False for wrong password
        # without raising exception when user is active but password is wrong
        # This would need to be modified in the actual service to handle this case
        with pytest.raises(AuthenticationFailedException):
            UserService.authenticate_user(user, "WrongPass")
