"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, items

router = APIRouter()

router.include_router(items.router, prefix="/items", tags=["items"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(health.router, prefix="/health", tags=["health"])

