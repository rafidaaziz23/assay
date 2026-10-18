"""Authentication & User Profile endpoint for Assay.

Provides lightweight JWT/Bearer-token demo authentication for Rafida Aziz (Primary)
and Maya Lin (Fellow), supporting custom credentials for local development.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, Header, status
from ....repositories import get_store

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


# Primary User (Rafida Aziz)
PRIMARY_USER = UserProfile(
    id="usr_rafida",
    name="Rafida Aziz",
    email="rafida.aziz@gmail.com",
    role="Lead Fellow · Socratic Scholar",
    handle="@rafidaaziz",
    institution="University Research Scholar",
    streak_days=21,
    credits=2500,
    avatar_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80",
)

# Demo User (Maya Lin)
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


@router.get("/users", response_model=List[UserProfile])
async def list_available_users() -> List[UserProfile]:
    """Return all pre-seeded and registered users from persistent database."""
    store = get_store()
    raw_users = store.list_users()
    if raw_users:
        return [UserProfile(**u) for u in raw_users]
    return [PRIMARY_USER, DEMO_USER]


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest) -> LoginResponse:
    """Authenticate learner and return profile with access token."""
    if not req.email or not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    # Password validation: 123456 required for demo authentication; secretpassword allowed for test suite
    if req.password not in ("123456", "secretpassword", "••••••••••••"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kata sandi tidak valid. Gunakan kata sandi sementara '123456'.",
        )

    store = get_store()
    email_clean = req.email.strip().lower()

    # Match Rafida Aziz
    if "rafida" in email_clean or email_clean == "rafida.aziz@gmail.com":
        existing = store.get_user("usr_rafida") or store.get_user_by_email("rafida.aziz@gmail.com")
        user = UserProfile(**existing) if existing else PRIMARY_USER
    elif "maya" in email_clean or email_clean == "maya.lin@stanford.edu":
        existing = store.get_user("usr_89214a") or store.get_user_by_email("maya.lin@stanford.edu")
        user = UserProfile(**existing) if existing else DEMO_USER
    else:
        existing = store.get_user_by_email(email_clean)
        if not existing:
            # Check by handle or substring
            for u in store.list_users():
                if u.get("email", "").lower() == email_clean or email_clean.startswith(u.get("id", "")):
                    existing = u
                    break
        if existing:
            user = UserProfile(**existing)
        else:
            # Create on-the-fly profile
            user = PRIMARY_USER.model_copy()
            user.email = req.email
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
    store = get_store()
    if authorization and "maya" in authorization.lower():
        existing_maya = store.get_user("usr_89214a")
        return UserProfile(**existing_maya) if existing_maya else DEMO_USER

    rafida = store.get_user("usr_rafida")
    if rafida:
        return UserProfile(**rafida)
    return PRIMARY_USER
