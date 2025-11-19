"""Authentication utilities (legacy - for backward compatibility)"""
from app.core.security import get_password_hash, verify_password

# Mock user DB (replace with real DB in production)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": get_password_hash("secret"),
    }
}

