import uuid
import json
import asyncio
from fastapi import APIRouter, Header, UploadFile, File, Form, Depends
from typing import Optional
from sse_starlette.sse import EventSourceResponse

from ....schemas.intake import RolesResponse, IntakeRequest, IntakeResponse, SEED_ROLES
from ....schemas.checklist import ChecklistResponse, ChecklistGenerateRequest, ChecklistUpdateRequest
from ....schemas.syllabus import SyllabusRequest, SyllabusResponse
from ....core.state_machine import store
from ....core.fallback import CACHED_CHECKLIST, CACHED_SYLLABUS, CHAPTER_CONTENTS

router = APIRouter()

@router.get("/roles", response_model=RolesResponse)
async def get_roles():
    """Returns fixed seed roles + Others option (PRD §3 Step 1, ADR 004)."""
    return RolesResponse(roles=SEED_ROLES, others_option="Others")

@router.post("/intake", response_model=IntakeResponse, status_code=201)
async def create_intake(
    req: IntakeRequest,
    x_demo_mode: Optional[str] = Header(None)
):
    session_id = f"sess_{uuid.uuid4().hex[:6]}"
    is_custom = req.role not in SEED_ROLES
    store.create_session(
        session_id=session_id,
        intent=req.intent,
        role=req.custom_role if is_custom and req.custom_role else req.role,
        has_doc=bool(req.document)
    )
    return IntakeResponse(
        session_id=session_id,
        intent=req.intent,
        role=req.role,
        has_document=bool(req.document),
        available_roles=SEED_ROLES,
        suggested_others=is_custom,
        next=f"POST /api/v1/intake/{session_id}/checklist"
    )

@router.post("/intake/{sessionId}/checklist")
async def generate_checklist(
    sessionId: str,
    req: Optional[ChecklistGenerateRequest] = None,
    x_demo_mode: Optional[str] = Header(None)
):
    """Generates topics based on intent, role, and optional document."""
    session = store.get_session(sessionId)
    role = session["role"] if session else "Frontend"

    # Streaming support if requested (SSE)
    if req and req.stream:
        async def event_generator():
            for item in CACHED_CHECKLIST:
                await asyncio.sleep(0.3)
                yield {
                    "event": "checklist.partial",
                    "data": json.dumps(item)
                }
            yield {
                "event": "checklist.done",
                "data": json.dumps({"session_id": sessionId, "status": "complete"})
            }
        return EventSourceResponse(event_generator())

    return ChecklistResponse(
        session_id=sessionId,
        role=role,
        source="document+role",
        checklist=CACHED_CHECKLIST
    )

@router.put("/intake/{sessionId}/checklist")
async def update_checklist(sessionId: str, req: ChecklistUpdateRequest):
    return {
        "session_id": sessionId,
        "selected_item_ids": req.selected_item_ids,
        "status": "updated"
    }

@router.post("/intake/{sessionId}/syllabus", response_model=SyllabusResponse, status_code=201)
async def synthesize_syllabus(
    sessionId: str,
    req: Optional[SyllabusRequest] = None,
    x_demo_mode: Optional[str] = Header(None)
):
    syllabus_id = f"syl_{uuid.uuid4().hex[:4]}"
    
    # Register chapters in state machine store
    for ch in CACHED_SYLLABUS["chapters"]:
        store.chapters[ch["chapter_id"]] = {
            **ch,
            "session_id": sessionId,
            "content_markdown": CHAPTER_CONTENTS.get(ch["chapter_id"], {}).get("content_markdown", "")
        }

    return SyllabusResponse(
        session_id=sessionId,
        syllabus_id=syllabus_id,
        title=CACHED_SYLLABUS["title"],
        source_mode=CACHED_SYLLABUS["source_mode"],
        total_chapters=CACHED_SYLLABUS["total_chapters"],
        chapters=CACHED_SYLLABUS["chapters"]
    )
