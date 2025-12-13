import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.controller import api_router
from app.core.logging import register_logger

from .error.exception_handlers import register_all_exception_handlers

app = FastAPI(title="FastAPI Server", version="1.0.0")

register_logger(app)

# Register all exception handlers (both domain and generic)
register_all_exception_handlers(app)

add_pagination(app)

# Include the routers
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
