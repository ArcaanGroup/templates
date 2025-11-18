"""Unit tests for authentication domain models"""

import pytest
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.domain.exceptions.auth_exceptions import (
    InvalidEmailException,
    InvalidPasswordException,
    InvalidUsernameException,
)


class TestUserEntity:
    """Test cases for User entity"""

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)

        assert user.username == username
        assert user.email == email
        assert user.password == password
        assert user.is_active is True

    def test_update_username(self):
        """Test updating user's username"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)
        new_username = Username("newuser")
        user.update_username(new_username)

        assert user.username == new_username

    def test_update_email(self):
        """Test updating user's email"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)
        new_email = Email("new@example.com")
        user.update_email(new_email)

        assert user.email == new_email

    def test_update_password(self):
        """Test updating user's password"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)
        new_password = Password("NewTestPass456")
        user.update_password(new_password)

        assert user.password == new_password

    def test_deactivate_user(self):
        """Test deactivating a user"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)
        user.deactivate()

        assert user.is_active is False

    def test_activate_user(self):
        """Test activating a user"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password, is_active=False)
        user.activate()

        assert user.is_active is True

    def test_verify_password(self):
        """Test password verification"""
        username = Username("testuser")
        email = Email("test@example.com")
        password = Password("TestPass123")

        user = User(username=username, email=email, password=password)

        assert user.verify_password("TestPass123") is True
        assert user.verify_password("WrongPass") is False


class TestEmailValueObject:
    """Test cases for Email value object"""

    def test_create_valid_email(self):
        """Test creating a valid email"""
        email = Email("test@example.com")
        assert str(email) == "test@example.com"

    def test_create_invalid_email(self):
        """Test creating an invalid email"""
        with pytest.raises(InvalidEmailException):
            Email("invalid-email")

    def test_email_equality(self):
        """Test email equality (case insensitive)"""
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")

        assert email1 == email2

    def test_email_hash(self):
        """Test email hashing"""
        email = Email("test@example.com")
        hash_value = hash(email)

        assert isinstance(hash_value, int)


class TestUsernameValueObject:
    """Test cases for Username value object"""

    def test_create_valid_username(self):
        """Test creating a valid username"""
        username = Username("testuser")
        assert str(username) == "testuser"

    def test_create_invalid_username_short(self):
        """Test creating a username that's too short"""
        with pytest.raises(InvalidUsernameException):
            Username("ab")

    def test_create_invalid_username_long(self):
        """Test creating a username that's too long"""
        with pytest.raises(InvalidUsernameException):
            Username("a" * 21)  # 21 characters

    def test_create_invalid_username_format(self):
        """Test creating a username with invalid characters"""
        with pytest.raises(InvalidUsernameException):
            Username("user@invalid")

    def test_username_equality(self):
        """Test username equality (case insensitive)"""
        username1 = Username("testuser")
        username2 = Username("TESTUSER")

        assert username1 == username2

    def test_username_hash(self):
        """Test username hashing"""
        username = Username("testuser")
        hash_value = hash(username)

        assert isinstance(hash_value, int)


class TestPasswordValueObject:
    """Test cases for Password value object"""

    def test_create_valid_password(self):
        """Test creating a valid password"""
        password = Password("TestPass123")
        assert password.verify("TestPass123") is True

    def test_create_invalid_password_short(self):
        """Test creating a password that's too short"""
        with pytest.raises(InvalidPasswordException):
            Password("weak")

    def test_create_invalid_password_no_uppercase(self):
        """Test creating a password without uppercase letter"""
        with pytest.raises(InvalidPasswordException):
            Password("testpass123")

    def test_create_invalid_password_no_lowercase(self):
        """Test creating a password without lowercase letter"""
        with pytest.raises(InvalidPasswordException):
            Password("TESTPASS123")

    def test_create_invalid_password_no_digit(self):
        """Test creating a password without digit"""
        with pytest.raises(InvalidPasswordException):
            Password("TestPassword")

    def test_password_verification(self):
        """Test password verification"""
        password = Password("TestPass123")
        assert password.verify("TestPass123") is True
        assert password.verify("WrongPass") is False

