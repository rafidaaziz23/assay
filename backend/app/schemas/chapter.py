from typing import List, Optional
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

class SuggestionsResponse(BaseModel):
    selection: str
    suggested_questions: List[str]
