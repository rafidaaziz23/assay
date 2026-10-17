"""F6/F7/F8 — Gated chapter reader + inline Socratic ask (API-CONTRACTS section 2.4).

The backend owns the gate (DEV 2 breakdown F6). The frontend only reads ``next_locked``;
if this module ever stops maintaining it, the gate is empty and the product thesis
(unlock by proving reasoning) silently disappears.

**Honeypot does NOT change state** — it fills ``honeypot_score`` only. Stated here
because it is the invariant most likely to be broken by a later change.

F17 note: the ask is a live LLM call, so it carries the cached envelope too. The reader is
the page the demo spends the most time on, and a blank reply there would be the exact
"blank spinner" golden rule 1 forbids.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query

from ....core import fallback as fb
from ....core.state_machine import UNLOCK_THRESHOLD, store
from ....repositories import get_store
from ....schemas import app_addons
from ....schemas.chapter import (
    ChapterDetailResponse,
    SocraticAskRequest,
    SocraticAskResponse,
    SuggestionsResponse,
)
from ....services import engine

router = APIRouter()

# Statuses where the interview is offered: reading done, or retrying after a fail.
INTERVIEW_READY_STATUSES = ("ACTIVE_READING", "INTERVIEW", "NEEDS_REVIEW")


def _chapter_or_404(chapter_id: str) -> Dict[str, Any]:
    st = get_store()
    chapter = st.get_chapter(chapter_id)
    if chapter is None:
        st.load_from_disk()
        chapter = st.get_chapter(chapter_id)
    if chapter is None:
        from ....core.seeder import seed_store
        seed_store(st)
        chapter = st.get_chapter(chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapter_id}")
    return chapter


def _page_set(chapter: Dict[str, Any]) -> set:
    """Pages the chapter is allowed to cite: its anchors plus stored page records."""
    pages = {int(p) for p in (chapter.get("source_pages") or []) if p is not None}
    for page in chapter.get("pages") or []:
        if isinstance(page, dict) and page.get("page") is not None:
            pages.add(int(page["page"]))
    return pages


@router.get("/chapters/{chapterId}", response_model=ChapterDetailResponse)
async def get_chapter(chapterId: str) -> ChapterDetailResponse:
    """Chapter content + state. The gate is decided HERE, not by the client (F6)."""
    chapter = _chapter_or_404(chapterId)
    status = chapter.get("status", "LOCKED")
    nxt = store.next_chapter(chapterId)
    # `next_locked` mirrors the stored flag, refreshed on every state change
    # (repositories.refresh_next_locked) — never *only* derived per request, because a
    # derived gate races when two events land together and leaks the next chapter.
    # "Locked" = successor still LOCKED; a successor moved to ACTIVE_READING by
    # apply_score means this chapter's pass already opened the gate.
    next_locked = bool(nxt) and nxt.get("status") == "LOCKED"

    return ChapterDetailResponse(
        chapter_id=chapterId,
        title=chapter.get("title", ""),
        status=status,
        content_markdown=(
            chapter.get("content_markdown") or f"# {chapter.get('title', 'Chapter')}\n"
        ),
        source_pages=list(chapter.get("source_pages") or []),
        next_locked=next_locked,
        interview_available=status in INTERVIEW_READY_STATUSES,
        next_chapter_id=nxt["chapter_id"] if nxt else None,
        unlock_threshold=UNLOCK_THRESHOLD,
        gate_source=(
            f"chapter_status={status};next="
            f"{nxt['chapter_id'] + ':' + str(nxt.get('status')) if nxt else 'none'}"
        ),
    )


@router.post("/chapters/{chapterId}/ask", response_model=SocraticAskResponse)
async def socratic_ask(
    chapterId: str,
    req: SocraticAskRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> SocraticAskResponse:
    """Select-word -> Socratic counter-inquiry (F7).

    ``gave_direct_answer`` must stay ``false`` in the default mode: handing over the
    answer would contradict the product thesis (anti brain-rot).

    Every interaction is persisted — it is the engagement metric and the audit trail.
    """
    chapter = _chapter_or_404(chapterId)
    anchor = req.anchor.model_dump() if req.anchor else None
    active = fb.active_scenario(x_demo_mode, scenario)

    result = engine.socratic_ask(chapter, req.selected_text, req.question, anchor or {})
    if active:
        # Frozen reply on the cached path: the recording's reader beat must be identical
        # every take (F17). The anchor still drives the citation so the highlight matches.
        result = fb.cached_ask(anchor)

    # Only cite a page the document actually has: a citation to a non-existent page is
    # the same class of false anchor the honeypot verdict exists to expose (F4).
    pages = _page_set(chapter)
    citations = []
    for citation in result.get("citations") or []:
        page = citation.get("page")
        if page is None or not pages or int(page) in pages:
            citations.append(citation)

    page_verified = False
    if anchor and anchor.get("page") is not None:
        page_verified = int(anchor["page"]) in pages

    recorded = get_store().add_ask_interaction(chapterId, {
        "kind": "ask",
        "session_id": req.session_id,
        "selected_text": req.selected_text,
        "question": req.question,
        "anchor": anchor,
        "gave_direct_answer": bool(result.get("gave_direct_answer")),
    })

    return SocraticAskResponse(
        mode=result.get("mode", "socratic"),
        reply=result.get("reply", ""),
        hint_level=max(1, min(3, int(result.get("hint_level", 1)))),
        citations=citations,
        gave_direct_answer=bool(result.get("gave_direct_answer", False)),
        interaction_id=f"ask_{recorded['at_ms'] % 10**6:06d}",
        page_verified=page_verified,
        engine=app_addons.engine_meta(not active)["engine"],
        fallback=fb.cached_response(active) if active else None,
    )


@router.get("/chapters/{chapterId}/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    chapterId: str,
    selection: str = Query(..., min_length=1, description="Selected phrase"),
) -> SuggestionsResponse:
    """Three relevant questions for a multi-word selection (F8)."""
    chapter = _chapter_or_404(chapterId)
    questions = [q for q in dict.fromkeys(engine.suggest_questions(chapter, selection))
                 if q.strip()][:3]

    recorded = get_store().add_ask_interaction(chapterId, {
        "kind": "suggestions",
        "selection": selection,
        "count": len(questions),
    })

    return SuggestionsResponse(
        selection=selection,
        suggested_questions=questions,
        interaction_id=f"sug_{recorded['at_ms'] % 10**6:06d}",
    )
