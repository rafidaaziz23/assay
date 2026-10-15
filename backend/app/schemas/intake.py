"""Intake & role selector schemas (API-CONTRACTS section 2.1, F1).

Additive DEV 2 fields are marked; they are all Optional with defaults so DEV 1's
TypeScript types keep working without a frontend deploy (see app_addons.py).
"""
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

# Fixed seed taxonomy (ADR 004 section 2.1). Single source for `GET /roles`.
SEED_ROLES = [
    "Frontend",
    "Backend",
    "Fullstack",
    "DevOps",
    "Data/ML",
    "Mobile",
    "QA/Test",
    "Security",
    "System Design",
]

OTHERS = "Others"


class RolesResponse(BaseModel):
    roles: List[str] = SEED_ROLES
    others_option: str = OTHERS


class IntakeRequest(BaseModel):
    intent: str = Field(..., description="What the user wants to learn")
    role: str = Field(..., description="Role selected from the seed list, or 'Others'")
    role_is_custom: bool = False
    custom_role: Optional[str] = None
    # The frontend sends the *file name* (it does not upload multipart); a real PDF or
    # raw-text document arrives via ``POST /intake/{id}/document``.
    document: Optional[str] = None

    @field_validator("intent")
    @classmethod
    def intent_needs_three_words(cls, value: str) -> str:
        words = [w for w in (value or "").split() if w.strip()]
        if len(words) < 3:
            raise ValueError("intent must contain at least 3 words")
        return value


class IntakeResponse(BaseModel):
    session_id: str
    intent: str
    role: str
    role_is_custom: bool = False
    custom_role: Optional[str] = None
    has_document: bool
    available_roles: List[str]
    suggested_others: bool = False
    next: str
    # ── DEV 2 additions ──
    engine: Optional[str] = None
    cache: Optional[dict[str, Any]] = None


class DocumentUploadResponse(BaseModel):
    """Result of page-anchored ingest (F4). ``pages`` is the count, not the content."""

    session_id: str
    document_name: str
    source_mode: str
    total_pages: int
    pages: List[int]
    char_count: int
    next: str
    engine: Optional[str] = None
