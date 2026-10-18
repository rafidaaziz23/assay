"""F6/F7/F8 — Chapter reader + inline Socratic ask (API-CONTRACTS section 2.4)."""
from typing import Any, List, Optional

from pydantic import BaseModel

from .syllabus import ChapterStatus


class ChapterDetailResponse(BaseModel):
    chapter_id: str
    title: str
    status: ChapterStatus
    content_markdown: str
    source_pages: List[int] = []
    next_locked: bool = True
    interview_available: bool = True
    # DEV 2 additions so the gate is auditable from the UI instead of guessed from
    # `status`: `gate_source` names what the backend checked (F6 note).
    next_chapter_id: Optional[str] = None
    unlock_threshold: int = 75
    gate_source: Optional[str] = None


class TextAnchor(BaseModel):
    page: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


class SocraticAskRequest(BaseModel):
    session_id: str
    selected_text: str
    question: str
    anchor: Optional[TextAnchor] = None


class Citation(BaseModel):
    kind: str
    page: Optional[int] = None


class SocraticAskResponse(BaseModel):
    mode: str = "socratic"
    reply: str
    hint_level: int = 1
    citations: List[Citation] = []
    gave_direct_answer: bool = False
    # DEV 2 additions: the interaction is persisted for the engagement metric and for
    # audit (F7), so echo its id; `page_verified` says whether the anchor resolved to a
    # page of the uploaded document.
    interaction_id: Optional[str] = None
    page_verified: Optional[bool] = None
    engine: Optional[str] = None
    # F17: the ask is a live model call, so the reader page carries the cached envelope
    # like every other AI-backed endpoint (API-CONTRACTS section 3).
    fallback: Optional[dict] = None


class SuggestionsResponse(BaseModel):
    selection: str
    suggested_questions: List[str]
    interaction_id: Optional[str] = None
