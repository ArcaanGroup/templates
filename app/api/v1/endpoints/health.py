"""Health check endpoints"""
from fastapi import APIRouter

from app.schema.response import StandardResponse, success

router = APIRouter()


@router.get("/", response_model=StandardResponse[dict])
async def health_check():
    """Basic health check"""
    return success({"status": "healthy"}, message="Service is healthy")


@router.get("/ready", response_model=StandardResponse[dict])
async def readiness_check():
    """Readiness probe"""
    # TODO: Add database connectivity check
    return success({"status": "ready"}, message="Service is ready")


@router.get("/live", response_model=StandardResponse[dict])
async def liveness_check():
    """Liveness probe"""
    return success({"status": "alive"}, message="Service is alive")

