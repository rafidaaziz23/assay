import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Assay - Active Socratic Learning Engine"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Google AI
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    # Never default to a retired ID: the container has no .env (see .dockerignore),
    # so whatever is hardcoded here is what production uses unless injected.
    # gemini-2.5-flash now returns 404 NOT_FOUND ("no longer available to new users").
    # gemini-3-flash-preview is 20 req/day on the free tier; flash-lite is 500/day.
    # See ai/_client.py for the measured quota table.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    GEMINI_PRO_MODEL: str = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview")
    
    # Demo & Resilience Mode ('live' or 'cached')
    DEMO_MODE: str = os.getenv("DEMO_MODE", "cached")
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
