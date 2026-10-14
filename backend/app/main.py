from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1.router import api_router

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

# Demo Mode Middleware: Injects header flag for offline zero-crash resilience
@app.middleware("http")
async def demo_mode_middleware(request: Request, call_next):
    # Check if header or env forced cached demo mode
    is_cached_demo = (
        request.headers.get("x-demo-mode") == "cached" or
        settings.DEMO_MODE == "cached"
    )
    response = await call_next(request)
    if is_cached_demo:
        response.headers["X-Assay-Resilience-Mode"] = "LOCAL_DETERMINISTIC_CACHE"
    return response

# Mount API v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "engine": "Google Gemini 2.5 Flash",
        "demo_mode": settings.DEMO_MODE
    }

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
