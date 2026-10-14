from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional

from ....schemas.chapter import (
    ChapterDetailResponse,
    SocraticAskRequest,
    SocraticAskResponse,
    SuggestionsResponse
)
from ....core.state_machine import store
from ....core.fallback import CHAPTER_CONTENTS
from ....services.gemini_service import gemini_service

router = APIRouter()

@router.get("/chapters/{chapterId}", response_model=ChapterDetailResponse)
async def get_chapter(chapterId: str):
    # Lookup in store or fallback
    ch_data = store.chapters.get(chapterId) or CHAPTER_CONTENTS.get(chapterId)
    if not ch_data:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return ChapterDetailResponse(
        chapter_id=chapterId,
        title=ch_data["title"],
        status=ch_data.get("status", "LOCKED"),
        content_markdown=ch_data.get("content_markdown", "# No content available"),
        source_pages=ch_data.get("source_pages", [1]),
        next_locked=ch_data.get("next_locked", True),
        interview_available=ch_data.get("status") in ["ACTIVE_READING", "INTERVIEW"]
    )

@router.post("/chapters/{chapterId}/ask", response_model=SocraticAskResponse)
async def socratic_ask(
    chapterId: str,
    req: SocraticAskRequest,
    x_demo_mode: Optional[str] = Header(None)
):
    """
    Inline Socratic Ask: Select-word -> counter-inquiry.
    Guarantees 'gave_direct_answer: false' as evidence of Anti-AI-Brain-Rot manifesto.
    """
    reply = gemini_service.generate_socratic_reply(req.selected_text, req.question)
    return SocraticAskResponse(**reply)

@router.get("/chapters/{chapterId}/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    chapterId: str,
    selection: str = Query(..., description="Selected phrase from chapter")
):
    """Generates 3 inquiry questions when multi-word selection is detected."""
    suggestions = [
        f"Why is '{selection}' considered an architectural tradeoff rather than a free optimization?",
        f"How does the engine maintain invariant state when '{selection}' encounters asynchronous interruption?",
        f"Under what specific edge conditions does '{selection}' degrade to quadratic complexity?"
    ]
    return SuggestionsResponse(
        selection=selection,
        suggested_questions=suggestions
    )
