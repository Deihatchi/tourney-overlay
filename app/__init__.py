"""FastAPI application factory for SF Overlay2."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router as api_router
from app.routes.overlays import router as overlay_router
from app.routes.websocket_routes import router as ws_router
from app.template_env import STATIC_DIR


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="SF Tournament Overlay", version="2.0.0")

    # CORS - allow all origins for local network access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Include routers
    app.include_router(api_router, prefix="/api")
    app.include_router(overlay_router)
    app.include_router(ws_router)

    return app
