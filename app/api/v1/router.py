"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, permissions, roles, users, user_roles

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
router.include_router(roles.router, prefix="/roles", tags=["roles"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(user_roles.router, prefix="/users", tags=["user-roles"])
