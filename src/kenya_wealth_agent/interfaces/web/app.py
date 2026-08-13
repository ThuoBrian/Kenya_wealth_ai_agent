"""FastAPI application for the Kenya Wealth Agent web interface."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from kenya_wealth_agent.infrastructure.logging import configure_logging
from kenya_wealth_agent.interfaces.web.dependencies import get_components
from kenya_wealth_agent.interfaces.web.routers import chat, history, tools

logger = structlog.get_logger()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add baseline HTTP security headers to every response."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Attach security headers and continue processing the request."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Permissions-Policy is intentionally kept minimal; expand when needed.
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response


def _find_web_dir() -> Path | None:
    """Locate the static web assets directory.

    The web UI lives at the repository root in a ``web`` folder.  When the
    package is installed this directory may not be present, in which case the
    API still works but the SPA is not served.
    """
    candidates = [
        Path(__file__).resolve().parents[4] / "web",
        Path.cwd() / "web",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan hook: configure logging and build components."""
    settings = get_components().settings
    configure_logging(log_level=settings.log_level, structured=settings.structured_logs)
    logger.info("web_app_startup", version=settings.version, model=settings.model)
    yield
    logger.info("web_app_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_components().settings

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["60/minute"],
        enabled=settings.enable_rate_limiting,
    )

    app = FastAPI(
        title="Kenya Wealth Agent",
        description="AI-powered financial advisor for the Kenyan market",
        version=settings.version,
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router, prefix="/api")
    app.include_router(tools.router, prefix="/api")
    app.include_router(history.router, prefix="/api")

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Liveness probe for load balancers and orchestrators."""
        return {"status": "ok"}

    web_dir = _find_web_dir()
    if web_dir:
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="static")
    else:
        logger.warning("web_assets_not_found", message="Static web assets not found")

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Return a JSON error for unhandled exceptions."""
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()
