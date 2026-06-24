"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .api import api_router
from .core.config import settings
from .core.logging_config import LoggingConfig, get_logger
from .database import init_db, close_db

# Initialize logging
LoggingConfig.setup_logging()
logger = get_logger(__name__)


class CORSExceptionMiddleware(BaseHTTPMiddleware):
    """Custom middleware to ensure CORS headers are added to all responses, including errors.

    This middleware wraps the response to ensure CORS headers are present even when
    an exception occurs and a 500 error is returned.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("Origin")
        
        try:
            response = await call_next(request)
        except Exception as e:
            # Log the exception
            logger.exception("Unhandled exception: %s", e)
            # Create error response with CORS headers
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"},
            )
        
        # Add CORS headers to all responses if origin is allowed
        if origin and origin in settings.CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(
                settings.CORS_ALLOW_CREDENTIALS
            ).lower()
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                settings.CORS_ALLOW_METHODS
            )
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                settings.CORS_ALLOW_HEADERS
            )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up %s v%s", settings.APP_NAME, settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down %s", settings.APP_NAME)
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cryptocurrency Signal Analysis Platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS - Custom middleware first to ensure headers on all responses (including errors)
app.add_middleware(CORSExceptionMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check_root() -> dict[str, str]:
    """Root health check endpoint.

    Returns:
        Health status
    """
    return {"status": "ok"}
