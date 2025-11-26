"""API endpoints"""

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import health
from app.api.v1.endpoints import permissions
from app.api.v1.endpoints import roles
from app.api.v1.endpoints import users

__all__ = [
    "auth",
    "health",
    "permissions",
    "roles",
    "users"
]
