from fastapi import APIRouter

from app.models.responses import StandardResponse, success

# Create router with prefix and tags
default_router = APIRouter(tags=["default"])


@default_router.get("/", response_model=StandardResponse)
async def root():
    """
    Root endpoint to provide basic information about the API.
    """

    return success(
        "Welcome to FastAPI server!",
        payload={"title": "FastAPI Server", "version": "1.0.0"},
    )
