"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from choreboss.config import get_config
from api.routers import auth, chores, people, web


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    # Startup
    print("🚀 ChoreBoss API starting...")
    yield
    # Shutdown
    print("🛑 ChoreBoss API shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance.
    """
    config = get_config()
    repo_root = Path(__file__).resolve().parents[1]

    app = FastAPI(
        title="ChoreBoss API",
        description="Household chore tracker API",
        version="2.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=config.secret_key,
        same_site="lax",
        https_only=False,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "10.0.0.28", "10.0.0.22", "10.0.0.81", "*"],
    )

    app.mount(
        "/static",
        StaticFiles(directory=str(repo_root / "web" / "static")),
        name="static",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(web.router, tags=["web"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(chores.router, prefix="/api/chores", tags=["chores"])
    app.include_router(people.router, prefix="/api/people", tags=["people"])

    @app.get("/api/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            dict: Status message.
        """
        return {"status": "ok"}

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Render browser-friendly auth errors while preserving API JSON."""
        if exc.status_code == 401 and not request.url.path.startswith("/api/"):
            return RedirectResponse(url="/login", status_code=303)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
