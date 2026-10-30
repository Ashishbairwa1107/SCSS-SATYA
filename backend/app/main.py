import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.security import sanitize_exception
from app.database.session import engine, Base

# Import all models to ensure metadata registration
import app.database.models

# Routers
from app.api.health import router as health_router
from app.api.cases import router as cases_router
from app.api.evidence import router as evidence_router
from app.api.examinations import router as examinations_router
from app.api.analysis import router as analysis_router
from app.api.reviews import router as reviews_router
from app.api.reports import router as reports_router
from app.api.specimens import router as specimens_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure directories and database tables
    settings.ensure_directories()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_FULL_TITLE,
    version=settings.VERSION,
    description=(
        "Institutional digital forensic image authenticity screening platform. "
        "Doctrine: 'The tool screens. The expert decides.'"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(health_router, prefix="/api")
app.include_router(cases_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(examinations_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(specimens_router, prefix="/api")

# Global Exception Handler for safe messaging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    safe_msg = sanitize_exception(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Processing Error",
            "detail": safe_msg,
            "path": request.url.path,
        }
    )

# Static assets & SPA fallback
dist_dir = settings.FRONTEND_DIST_DIR
assets_dir = dist_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa_or_fallback(full_path: str):
    """
    Serve SPA production frontend with client-side routing fallback,
    or return informational page if dist is not yet built.
    """
    # Prevent intercepting docs or api
    if full_path.startswith("api/") or full_path in ["docs", "redoc", "openapi.json"]:
        return JSONResponse(status_code=404, content={"detail": "Not Found"})

    index_file = dist_dir / "index.html"
    if index_file.exists():
        # Check if requesting a specific static file in dist
        file_candidate = dist_dir / full_path
        if file_candidate.exists() and file_candidate.is_file():
            return FileResponse(file_candidate)
        return FileResponse(index_file)

    # Informative response when frontend is not yet built
    return JSONResponse(
        status_code=200,
        content={
            "platform": settings.PROJECT_FULL_TITLE,
            "version": settings.VERSION,
            "doctrine": settings.DOCTRINE,
            "status": "Backend API is operational.",
            "api_documentation": "/docs",
            "redoc": "/redoc",
            "frontend_note": "Frontend build not yet detected in frontend/dist. Run 'npm run build' in /frontend.",
        }
    )
