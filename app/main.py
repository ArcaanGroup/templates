from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.items import router as items_router
from app.repositories.items_repository import InMemoryItemsRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared resources once
    app.state.items_repo = InMemoryItemsRepository()
    try:
        yield
    finally:
        # Clean up if needed (close DB connections, etc.)
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="FastAPI Starter Boilerplate",
        version="0.1.0",
    )

    @app.get("/ping", tags=["health"], summary="Health check")
    async def ping():
        return {"status": "ok"}

    app.include_router(items_router)
    return app


app = create_app()
