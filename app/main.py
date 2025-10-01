from fastapi import FastAPI
from app.api.items import router as items_router


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
