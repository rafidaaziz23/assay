"""Authentication & User Profile endpoint for Assay.

Provides lightweight JWT/Bearer-token demo authentication for Maya Lin (Fellow)
and supports custom credentials for local development.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Header, status

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


class LoginRequest(BaseModel):
    email: str
    password: str
    remember: bool = True


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    handle: str
    institution: str
    streak_days: int
    credits: int
    avatar_url: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    expires_in: int = 86400


# Demo Default User (Maya Lin from approved Figma design)
DEMO_USER = UserProfile(
    id="usr_89214a",
    name="Maya Lin",
    email="maya.lin@stanford.edu",
    role="Fellow",
    handle="@mayalin",
    institution="Stanford University",
    streak_days=14,
    credits=1250,
    avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
)


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest) -> LoginResponse:
    """Authenticate learner and return profile with access token."""
    # Permissive auth for demo; validate presence
    if not req.email or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    # In demo mode, derive user from email or fallback to Maya Lin
    user = DEMO_USER.model_copy()
    if req.email and "@" in req.email:
        user.email = req.email
        if "maya" not in req.email.lower():
            user.name = req.email.split("@")[0].replace(".", " ").title()
            user.handle = f"@{req.email.split('@')[0]}"

    return LoginResponse(
        access_token=f"assay_jwt_{int(time.time())}_{user.id}",
        token_type="bearer",
        user=user,
        expires_in=86400,
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> UserProfile:
    """Return currently authenticated learner profile."""
    return DEMO_USER
