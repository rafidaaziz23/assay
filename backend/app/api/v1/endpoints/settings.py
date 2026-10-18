"""Runtime Configuration & Calibration Settings endpoint.

Allows dynamic selection of the Socratic LLM engine, target cognitive rigor,
and adversarial honeypot sensitivity from the frontend settings screen.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Settings"])


class SettingsPayload(BaseModel):
    model: str = "gemini-3.1-flash-lite"
    rigor: str = "academic"
    fallacy_sensitivity: str = "balanced"
    audio_device: Optional[str] = "Default Microphone (High Definition Audio Device)"


# In-memory settings state
CURRENT_SETTINGS = SettingsPayload()


@router.get("", response_model=SettingsPayload)
async def get_settings() -> SettingsPayload:
    """Return active runtime reasoning engine settings."""
    return CURRENT_SETTINGS


@router.post("", response_model=SettingsPayload)
async def update_settings(payload: SettingsPayload) -> SettingsPayload:
    """Update runtime Socratic parameters."""
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = payload
    return CURRENT_SETTINGS
