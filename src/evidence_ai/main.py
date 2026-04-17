"""FastAPI application entrypoint for EvidenceAI.

Creates and configures the FastAPI application instance, registers routers,
sets up middleware (CORS, logging, rate limiting), and defines the health
check endpoint.

Run locally::

    uvicorn evidence_ai.main:app --reload --host 0.0.0.0 --port 8000

Or via Docker::

    docker compose up api
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from evidence_ai.api.routes import router as api_router
from evidence_ai.config import settings
from evidence_ai.db.database import close_db, init_db

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ANN001
    """Application lifespan: startup and shutdown events."""
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("EvidenceAI starting up (env=%s)", settings.app_env)
    await init_db()
    logger.info("Database connection pool initialized")
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    await close_db()
    logger.info("EvidenceAI shut down gracefully")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="EvidenceAI",
        description=(
            "AI-powered clinical evidence synthesis platform for FDA submissions. "
            "Automates systematic literature reviews for biotech and pharmaceutical "
            "companies — reducing cost from $141K/18 months to under $10K in weeks."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Compression ───────────────────────────────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Request timing middleware ─────────────────────────────────────────────
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: object) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)  # type: ignore[operator]
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        return response

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.api_prefix)

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["system"], summary="Health check")
    async def health_check() -> dict[str, str]:
        """Returns 200 OK if the service is running."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.app_env,
        }

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred. Please try again.",
                "request_id": request.headers.get("X-Request-ID"),
            },
        )

    return app


app = create_app()
