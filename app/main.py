import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.controller import api_router
from app.core.logging import register_logger

from .error.exception_handlers import register_all_exception_handlers

app = FastAPI(title="FastAPI Server", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add your production domain later
    ],
    allow_credentials=True,  # Required for cookies/auth
    allow_methods=["*"],  # Or specify: ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],  # Or specify headers you need
    expose_headers=["*"],  # Expose custom headers to browser
    max_age=600,  # Cache preflight requests for 10 minutes
)

register_logger(app)

# Register all exception handlers (both domain and generic)
register_all_exception_handlers(app)

add_pagination(app)

# Include the routers
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
