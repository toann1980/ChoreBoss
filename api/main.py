"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, chores, people


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
    app = FastAPI(
        title="ChoreBoss API",
        description="Household chore tracker API",
        version="2.0.0",
        lifespan=lifespan,
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

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
