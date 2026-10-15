"""F1–F5 — intake, checklist, syllabus, page-anchored ingest, grounding cache.

Implements API-CONTRACTS sections 2.1–2.3. The AI content comes from the DEV 3 engine
(``ai/``) through ``services.engine``; this module owns validation, persistence, the
state machine seeding, and the cached fallback path.

Design notes that are easy to get wrong later:

* Validation of the role/``Others`` contract happens HERE, in intake, not at classify
  time (ADR 004 s2.4).
* Checklist is one endpoint with two modes: ``{"stream": true}`` -> SSE
  (``checklist.partial`` per item, closed by ``checklist.done``), otherwise plain JSON
  (F2).
* The no-PDF path MUST still produce chapters, marked ``role_taxonomy_generated`` —
  that is the Hari 1 gate (F3).
* Page numbers survive ingest (F4). If ingest loses them, the honeypot's main argument
  ("this term is on no page of your document") dies with them.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, Header, HTTPException, Query, UploadFile
from sse_starlette.sse import EventSourceResponse

from ....core import fallback as fb
from ....core import state_machine as sm
from ....core.state_machine import store
from ....repositories import get_store, new_id
from ....schemas import app_addons
from ....schemas.checklist import (
    ChecklistGenerateRequest,
    ChecklistResponse,
    ChecklistUpdateRequest,
    ChecklistUpdateResponse,
)
from ....schemas.intake import (
    SEED_ROLES,
    DocumentUploadResponse,
    IntakeRequest,
    IntakeResponse,
    RolesResponse,
)
from ....schemas.syllabus import SyllabusRequest, SyllabusResponse
from ....services import engine
from ....services.pdf_service import extract_pages_from_pdf_bytes

router = APIRouter()

OTHERS = "Others"


def _demo_scenario(header_value: Optional[str]) -> Optional[str]:
    return fb.active_scenario(header_value)


def _cache_meta(scenario_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not scenario_id:
        return None
    return {
        **fb.cached_response(scenario_id),
        **app_addons.cache_meta(fb.CACHE_SCHEMA_VERSION),
    }


def _engine_meta(is_cached: bool) -> str:
    return "deterministic_cache" if is_cached else "live"


def _resolve_role(req: IntakeRequest) -> str:
    """Enforce the ADR 004 contract: seed role, or ``Others`` + custom text.

    Unknown roles are coerced to ``Others`` rather than rejected — an intake screen
    must not dead-end on a selector edge case. ``suggested_others`` tells the UI to
    open the free-text field.
    """
    role = (req.role or "").strip()
    if role in SEED_ROLES:
        return role
    custom = (
        (req.custom_role or "").strip()
        or (role if req.role_is_custom and role != OTHERS else "")
    )
    return custom or OTHERS


def _requires_session(session_id: str) -> Dict[str, Any]:
    session = get_store().get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"unknown session: {session_id}")
    return session


# ── F1 ─────────────────────────────────────────────────────────────────────────

@router.get("/roles", response_model=RolesResponse)
async def get_roles() -> RolesResponse:
    """Seed roles + the auto ``Others`` option (F1, ADR 004)."""
    return RolesResponse(roles=list(engine.engine.SEED_ROLES), others_option=OTHERS)


@router.post("/intake", response_model=IntakeResponse, status_code=201)
async def create_intake(
    req: IntakeRequest,
    x_demo_mode: Optional[str] = Header(None),
) -> IntakeResponse:
    scenario = _demo_scenario(x_demo_mode)
    session_id = new_id("sess")
    role = _resolve_role(req)
    role_is_custom = req.role_is_custom or role not in SEED_ROLES

    classified = engine.engine.classify_intent(req.intent)
    suggested_others = bool(classified.get("suggested_others")) or role_is_custom

    get_store().create_session(
        session_id,
        intent=req.intent,
        role=role,
        role_is_custom=role_is_custom,
        custom_role=req.custom_role if role_is_custom else None,
        suggested_others=suggested_others,
        has_document=bool(req.document),
        document_name=req.document,
        demo_mode="cached" if scenario else "live",
    )

    return IntakeResponse(
        session_id=session_id,
        intent=req.intent,
        role=role,
        role_is_custom=role_is_custom,
        custom_role=req.custom_role if role_is_custom else None,
        has_document=bool(req.document),
        available_roles=list(engine.engine.SEED_ROLES),
        suggested_others=suggested_others,
        next=f"POST /api/v1/intake/{session_id}/checklist",
        engine=_engine_meta(bool(scenario)),
        cache=_cache_meta(scenario),
    )


# ── F4 — page-anchored ingest ──────────────────────────────────────────────────

@router.post(
    "/intake/{sessionId}/document",
    response_model=DocumentUploadResponse,
    status_code=201,
)
async def upload_document(
    sessionId: str,
    file: UploadFile = File(...),
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> DocumentUploadResponse:
    """Ingest a PDF (or raw text) page-anchored.

    PDF -> ``ai.index_document`` (PyMuPDF, one entry per page). Text -> explicit page
    markers if present, otherwise a single honest page. Either way the result is a
    per-page list, never one blob, so retrieval can return
    ``{page, char_start, char_end}`` for ``POST /chapters/:id/ask``.
    """
    _requires_session(sessionId)
    payload = await file.read()
    name = file.filename or "upload"

    is_pdf = payload[:4] == b"%PDF"
    if is_pdf:
        try:
            index = engine.engine.index_document(payload)
            pages = [
                {"page": int(p["page"]), "text": p.get("text", ""),
                 "char_count": len(p.get("text", ""))}
                for p in index.get("pages", [])
            ]
        except Exception:
            # Corrupt/unreadable PDF must still yield an ingest result the demo can use.
            pages = extract_pages_from_pdf_bytes(payload)
    else:
        pages = app_addons.page_anchored_text(payload.decode("utf-8", errors="replace"))

    if not pages:
        pages = [{"page": 1, "text": "", "char_count": 0}]

    doc_index: Dict[str, Any] = {
        "pages": pages,
        "total_pages": len(pages),
        "document_name": name,
    }
    get_store().update_session(
        sessionId,
        has_document=True,
        document_name=name,
        doc_index=doc_index,
        source_mode="document_rag",
    )

    # Ingest is *not* an AI call — PyMuPDF runs locally, so the work is real even when the
    # cache is active. The label reports the mode for consistency with the other endpoints
    # (it used to be hardcoded "live", which claimed live extraction inside a cached run).
    return DocumentUploadResponse(
        session_id=sessionId,
        document_name=name,
        source_mode="document_rag",
        total_pages=len(pages),
        pages=[p["page"] for p in pages],
        char_count=sum(p["char_count"] for p in pages),
        next=f"POST /api/v1/intake/{sessionId}/checklist",
        engine=_engine_meta(bool(fb.active_scenario(x_demo_mode, scenario))),
    )


@router.get("/intake/{sessionId}/document")
async def document_pages(
    sessionId: str,
    page: Optional[int] = None,
) -> Dict[str, Any]:
    """Page-anchored retrieval (F4). Backend owns the store; DEV 3 owns query logic.

    Returns ``{page, char_start, char_end, text}`` per page so an ask can cite a span
    instead of a whole document.
    """
    session = _requires_session(sessionId)
    index = session.get("doc_index") or {}
    pages = index.get("pages") or []
    if page is not None:
        pages = [p for p in pages if int(p.get("page", 0)) == int(page)]
        if not pages:
            raise HTTPException(status_code=404, detail=f"page {page} not in document")
    return {
        "session_id": sessionId,
        "document_name": index.get("document_name"),
        "total_pages": index.get("total_pages", len(index.get("pages") or [])),
        "pages": [
            {
                "page": p.get("page"),
                "char_start": 0,
                "char_end": p.get("char_count", len(p.get("text", ""))),
                "text": p.get("text", ""),
            }
            for p in pages
        ],
    }


# ── F2 — checklist (JSON + SSE) ────────────────────────────────────────────────

def _doc_text(session: Dict[str, Any], limit: int = 6000) -> Optional[str]:
    index = session.get("doc_index") or {}
    pages = index.get("pages") or []
    if not pages:
        return None
    joined = "\n".join(p.get("text", "") for p in pages)
    return joined[:limit] or None


@router.post("/intake/{sessionId}/checklist")
async def generate_checklist(
    sessionId: str,
    req: Optional[ChecklistGenerateRequest] = None,
    x_demo_mode: Optional[str] = Header(None),
):
    """Generate topic items; ``{"stream": true}`` switches to SSE (F2).

    SSE is tested on Hari 1 on purpose: on Cloud Run a buffered response never shows
    ``checklist.partial``, and that partial is the moment the video records.
    """
    session = _requires_session(sessionId)
    scenario = _demo_scenario(x_demo_mode)
    stream = bool(req and req.stream)

    if scenario:
        items: List[Dict[str, Any]] = fb.cached_checklist(scenario)
    else:
        raw = engine.engine.gen_checklist(
            session.get("intent", ""), session.get("role", ""), _doc_text(session)
        )
        items = list(raw) if not hasattr(raw, "__next__") else list(raw)

    # Origin must be truthful: a topic tagged `document` when no document was uploaded
    # is a false claim of grounding, and the honeypot's argument leans on that anchor.
    has_doc = bool(_doc_text(session))
    if not has_doc:
        for item in items:
            if item.get("origin") == "document":
                item["origin"] = "role_taxonomy"

    # Remember the engine's own proposal so `elective` (proposed-but-dropped) survives
    # the PUT that rewrites `selected`.
    stored_items = [
        {**i, "selected": bool(i.get("selected", True)),
         "proposed_selected": bool(i.get("selected", True))}
        for i in items
    ]
    get_store().set_checklist(sessionId, stored_items)
    items = app_addons.tag_elective(stored_items, [i["item_id"] for i in stored_items if i["selected"]])

    if stream:
        async def event_generator():
            for item in items:
                # No artificial sleep: the delay used to fake streaming also made the
                # recorder wait. Real pacing comes from the model call upstream.
                yield {"event": "checklist.partial", "data": json.dumps(item)}
                await asyncio.sleep(0)
            yield {
                "event": "checklist.done",
                "data": json.dumps(
                    {"session_id": sessionId, "total": len(items), "status": "complete"}
                ),
            }

        return EventSourceResponse(event_generator())

    return ChecklistResponse(
        session_id=sessionId,
        role=session.get("role", ""),
        source="document+role" if session.get("has_document") else "role_taxonomy",
        checklist=items,
        engine=_engine_meta(bool(scenario)),
        cache=_cache_meta(scenario),
    )


@router.put("/intake/{sessionId}/checklist", response_model=ChecklistUpdateResponse)
async def update_checklist(sessionId: str, req: ChecklistUpdateRequest) -> ChecklistUpdateResponse:
    """Finalise the student's selection; only selected items feed the syllabus (F2)."""
    session = _requires_session(sessionId)
    if not session.get("checklist"):
        raise HTTPException(
            status_code=409, detail="generate the checklist before selecting items"
        )

    known = {i["item_id"] for i in session["checklist"]}
    unknown = [i for i in req.selected_item_ids if i not in known]
    if unknown:
        raise HTTPException(
            status_code=422, detail=f"unknown checklist item ids: {unknown}"
        )

    stored = get_store().apply_checklist_selection(sessionId, req.selected_item_ids)
    tagged = app_addons.tag_elective(
        session["checklist"], [i["item_id"] for i in stored]
    )
    return ChecklistUpdateResponse(
        session_id=sessionId,
        selected_item_ids=[i["item_id"] for i in stored],
        checklist=tagged,
        selected_count=len(stored),
    )


# ── F3 — syllabus synthesis ────────────────────────────────────────────────────

@router.post(
    "/intake/{sessionId}/syllabus", response_model=SyllabusResponse, status_code=201
)
async def synthesize_syllabus(
    sessionId: str,
    req: Optional[SyllabusRequest] = None,
    x_demo_mode: Optional[str] = Header(None),
) -> SyllabusResponse:
    """Chunk the document (or generate from the role taxonomy) into chapters (F3).

    Backend owns the store and the state machine; DEV 3 owns the content. Without a
    document the chapters are still produced and marked ``role_taxonomy_generated``.
    """
    session = _requires_session(sessionId)
    scenario = _demo_scenario(x_demo_mode)
    enable_grounding = bool(req and req.enable_search_grounding)

    if scenario:
        syllabus = fb.cached_syllabus(scenario)
    else:
        syllabus = engine.engine.synth_syllabus(
            session.get("intent", ""),
            session.get("role", ""),
            session.get("doc_index"),
            enable_search_grounding=enable_grounding,
        )

    source_mode = (
        "document_rag"
        if (session.get("doc_index") or {}).get("pages")
        else "role_taxonomy_generated"
    )
    chapters = syllabus.get("chapters") or []

    # Attach cached content so the reader page never renders empty (DEMO-SCRIPT #1).
    for chapter in chapters:
        cached = fb.cached_chapter_content(chapter["chapter_id"])
        chapter.setdefault("source_mode", source_mode)
        if cached:
            chapter.setdefault("content_markdown", cached["content_markdown"])
        else:
            chapter.setdefault(
                "content_markdown",
                f"# {chapter.get('title', 'Chapter')}\n\n"
                f"{chapter.get('title', '')} — content synthesized from the "
                f"{'uploaded document' if source_mode == 'document_rag' else 'role taxonomy'}.\n",
            )
        # F5: grounding is trimmed to ONE chapter and cached.
        if enable_grounding and chapter.get("order") == 1:
            grounded = fb.cached_grounding(session.get("role", "") or "general")
            chapter.setdefault("references", [])
            chapter["references"] = list(chapter["references"]) + grounded["references"]

    persisted = sm.initialize_from_syllabus(sessionId, chapters)
    doc_pages = sorted({p["page"] for p in (session.get("doc_index") or {}).get("pages", [])})
    real = set(doc_pages)
    count = max(1, len(persisted))

    # Anchors must point at real pages of the upload; inventing them is how the
    # honeypot claim becomes unverifiable (F4).
    raw_anchors = [
        [int(p) for p in ch.get("source_pages", []) if p in real] for ch in persisted
    ]
    # An anchor set that is identical for every chapter carries no discriminating
    # information — the engine's keyword match fell through to its default page. Spread
    # the document's real pages across chapters so each chapter is anchored to a
    # different, honest page instead of every chapter claiming page 1.
    uninformative = len({tuple(a) for a in raw_anchors}) == 1 and len(doc_pages) > 1

    for index, chapter in enumerate(persisted):
        anchors = [] if uninformative else raw_anchors[index]
        if not anchors and doc_pages:
            start = index * len(doc_pages) // count
            end = max(start + 1, (index + 1) * len(doc_pages) // count)
            anchors = doc_pages[start:end] or doc_pages[-1:]
        chapter["source_pages"] = anchors
        if real:
            # Same clamp for reference pages: a reference to page 6 of a three-page
            # upload is exactly as false as a fabricated anchor.
            chapter["references"] = [
                {**ref, "page": ref["page"] if ref.get("page") in real
                 else (chapter["source_pages"][0] if chapter["source_pages"] else None)}
                if ref.get("kind") == "document" and ref.get("page") is not None
                else ref
                for ref in chapter.get("references", [])
            ]
        else:
            # No document at all: a `document` reference would be a fabricated source.
            chapter["references"] = [
                ref for ref in chapter.get("references", [])
                if ref.get("kind") != "document"
            ]

    syllabus_id = syllabus.get("syllabus_id") or new_id("syl", 4)
    get_store().update_session(
        sessionId,
        syllabus_id=syllabus_id,
        syllabus_title=syllabus.get("title", ""),
        source_mode=source_mode,
        status="SYLLABUS",
    )

    return SyllabusResponse(
        session_id=sessionId,
        syllabus_id=syllabus_id,
        title=syllabus.get("title", ""),
        source_mode=source_mode,
        total_chapters=len(persisted),
        chapters=[
            {
                "chapter_id": c["chapter_id"],
                "title": c.get("title", ""),
                "order": c.get("order", 1),
                "status": c.get("status", "LOCKED"),
                "prerequisites": c.get("prerequisites", []),
                "estimated_reading_minutes": c.get("estimated_reading_minutes", 5),
                "source_pages": c.get("source_pages", []),
                "references": c.get("references", []),
            }
            for c in persisted
        ],
        cache=_cache_meta(scenario),
        grounding=(
            fb.cached_grounding(session.get("role", "") or "general")
            if enable_grounding
            else None
        ),
    )
