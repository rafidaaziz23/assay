"""F11/F12 — Focus Mode event ingest (API-CONTRACTS section 2.7, ADR 003).

Three rules are frozen and are enforced here rather than trusted to the client:

1. **``video_transmitted`` MUST be ``false``.** Only boolean events cross the wire;
   inference is on-device (ADR 003 s2.2). A payload carrying a blob is rejected — accepting
   it would make the privacy claim in the deck false. This check runs in the handler as
   well as in the pydantic schema, because the cached path and any replayed event log reach
   this logic with a plain dict and would bypass the model validator.
2. **Focus Mode is a signal, not an anti-cheat verdict.** The response reports
   ``integrity_flag`` and nothing stronger (PRD risk R5). It adjusts the score by three
   points at most and never blocks a chapter.
3. **Accessible Mode is not an error path.** Camera off -> ``assisted_unverified``, and the
   score is still computed (DEV 2 F11/F12). This is the path most likely to be written as a
   special case and then forgotten, so it has its own test.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query

from ....core import fallback as fb
from ....core.integrity import (
    VideoPayloadRejected,
    derive_integrity,
    validate_focus_payload,
)
from ....repositories import get_store
from ....schemas import app_addons
from ....schemas.focus import FocusEventsRequest, FocusEventsResponse, FocusSummary

router = APIRouter()


@router.post("/chapters/{chapterId}/focus-events", response_model=FocusEventsResponse)
async def record_focus_events(
    chapterId: str,
    req: FocusEventsRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> FocusEventsResponse:
    chapter = get_store().get_chapter(chapterId)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapterId}")

    payload = req.model_dump()
    try:
        validate_focus_payload(payload)
    except VideoPayloadRejected as exc:
        # 422, not 400: the body is well-formed JSON but violates the contract's privacy
        # invariant, which is exactly what FastAPI reserves 422 for.
        raise HTTPException(status_code=422, detail=str(exc))

    event_dicts = [e.model_dump() for e in req.events]
    get_store().add_focus_events(req.interview_id, event_dicts)

    active = fb.active_scenario(x_demo_mode, scenario)
    if active:
        result = fb.cached_focus(active)
    else:
        result = derive_integrity(event_dicts, accessible_mode=req.accessible_mode)

    # The flag is sticky per interview. A later clean batch must not erase an earlier
    # tab-blur, otherwise an integrity flag could be laundered away by sending one empty
    # batch right before finalize.
    flag = result["integrity_flag"]
    existing = get_store().get_focus_flag(req.interview_id)
    if existing is None or flag != "clean":
        get_store().set_focus_flag(req.interview_id, flag)

    return FocusEventsResponse(
        integrity_flag=flag,
        auto_blur=result["auto_blur"],
        summary=FocusSummary(**result["summary"]),
        integrity_score=app_addons.integrity_score(flag),
        accessible_mode=result.get("accessible_mode", req.accessible_mode),
        fallback=fb.cached_response(active) if active else None,
    )
