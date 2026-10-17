from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1.router import api_router
from .core import fallback as fb
from .core.seeder import seed_store

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Active Socratic Learning Engine - AI Builder Cup 2026 (Track 4)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development and mobile inspection
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo Mode Middleware: injects the resilience marker so the frontend's FallbackBadge can
# prove which path served the request — useful on camera and in a bug report.
@app.middleware("http")
async def demo_mode_middleware(request: Request, call_next):
    # Delegates to the same helper every endpoint uses. Reading `settings.DEMO_MODE`
    # directly here would go stale the moment the environment changes (settings is built
    # once at import), so the badge could claim "live" while everything was cached.
    is_cached_demo = fb.demo_mode_active(
        request.headers.get("x-demo-mode"), request.query_params.get("scenario")
    )
    response = await call_next(request)
    if is_cached_demo:
        response.headers["X-Assay-Resilience-Mode"] = fb.FALLBACK_SOURCE
    return response

# Mount API v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.on_event("startup")
def startup_seeder():
    """Seed InMemoryStore on server startup."""
    seed_store()

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "engine": "Google Gemini 2.5 Flash",
        # The live environment value, not the import-time snapshot: the demo needs to know
        # what this process is actually doing right now.
        "demo_mode": "cached" if fb.demo_mode_active() else "live",
        "cache_schema_version": fb.CACHE_SCHEMA_VERSION,
    }

@app.get("/health/cache", tags=["Health"])
async def cache_self_check():
    """R7: is the shipped cache still consistent with the current response schema?

    Cache that has drifted from the UI is silently worse than no cache: the recording runs
    on it, so the demo shows fields the frontend no longer expects. This is checkable
    rather than eyeballed, and the demo-safety step is `ok: true` before recording.
    """
    return fb.validate_cache()

@app.get("/", tags=["Root"])
async def root():
    return {
        "product": "Assay: The Active Socratic Learning Engine",
        "track": "Track 4: Media, Content & Digital Experiences",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
