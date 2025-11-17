"""Application entry point"""
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.utils.error import register_error_handlers

configure_logging()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Enterprise FastAPI template with Clean Architecture"
    )
    
    # Add pagination support
    add_pagination(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    app.include_router(api_v1_router, prefix="/api/v1")
    
    # Health check endpoints
    @app.get("/ping")
    async def ping():
        """Simple ping endpoint"""
        return "pong"
    
    @app.get("/error")
    async def error():
        """Test error endpoint"""
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    
    return app


app = create_app()

