"""F3 — Syllabus synthesis schemas (API-CONTRACTS section 2.3)."""
from typing import Any, List, Literal, Optional

from pydantic import BaseModel

ReferenceKind = Literal["document", "grounded_external"]
ChapterStatus = Literal[
    "LOCKED", "ACTIVE_READING", "INTERVIEW", "SCORED", "UNLOCKED", "NEEDS_REVIEW"
]
SourceMode = Literal["document_rag", "role_taxonomy_generated"]


class ReferenceItem(BaseModel):
    kind: ReferenceKind
    label: str
    page: Optional[int] = None
    url: Optional[str] = None
    verified: Optional[bool] = None
    cached: Optional[bool] = None


class ChapterMeta(BaseModel):
    chapter_id: str
    title: str
    order: int
    status: ChapterStatus = "LOCKED"
    prerequisites: List[str] = []
    estimated_reading_minutes: int
    source_pages: List[int] = []
    references: List[ReferenceItem] = []


class SyllabusRequest(BaseModel):
    enable_search_grounding: bool = False


class SyllabusResponse(BaseModel):
    session_id: str
    syllabus_id: str
    title: str
    source_mode: SourceMode
    total_chapters: int
    chapters: List[ChapterMeta]
    # DEV 2 additions.
    cache: Optional[dict[str, Any]] = None
    grounding: Optional[dict[str, Any]] = None
