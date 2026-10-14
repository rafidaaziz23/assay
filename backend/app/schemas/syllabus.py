from typing import List, Optional, Literal
from pydantic import BaseModel

ReferenceKind = Literal["document", "grounded_external"]
ChapterStatus = Literal["LOCKED", "ACTIVE_READING", "INTERVIEW", "SCORED", "UNLOCKED", "NEEDS_REVIEW"]

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
    source_mode: Literal["document_rag", "role_taxonomy_generated"]
    total_chapters: int
    chapters: List[ChapterMeta]
