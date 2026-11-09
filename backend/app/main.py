"""FastAPI app: JSON API under /api and, if built, the frontend as static files."""

from pathlib import Path

from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

from app import api
from app.config import PROJECT_ROOT

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"
# First path segments that never fall back to index.html.
NO_FALLBACK = {"api", "assets"}


class SPAStaticFiles(StaticFiles):
    """Static files with fallback to index.html, so client-side routes like /courses/1 work."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as error:
            # No fallback for unknown API paths (stay a JSON 404) and missing build assets
            # (a stale browser cache would otherwise get HTML instead of JS/CSS).
            if error.status_code != 404 or path.split("/", 1)[0] in NO_FALLBACK:
                raise
            return await super().get_response("index.html", scope)


def create_app(frontend_dist: Path = FRONTEND_DIST) -> FastAPI:
    app = FastAPI(title="Lernraum Cockpit")
    app.include_router(api.router)
    # In dev mode the frontend is served by Vite, so dist/ may not exist.
    if (frontend_dist / "index.html").is_file():
        app.mount("/", SPAStaticFiles(directory=frontend_dist, html=True), name="frontend")
    return app


app = create_app()
