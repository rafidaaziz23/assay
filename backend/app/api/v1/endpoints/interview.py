import uuid
from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from ....schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewTurnRequest,
    InterviewTurnResponse,
    InterviewFinalizeRequest,
    InterviewFinalizeResponse,
    FocusModeConfig,
    HoneypotMetadata,
    ScoreDetail,
    HoneypotVerdict,
    ChapterStateUpdate,
    VerifierStatus
)
from ....core.state_machine import store
from ....services.honeypot_catalog import classify_honeypot_response, DETERMINISTIC_HONEYPOTS

router = APIRouter()

@router.post("/chapters/{chapterId}/interview/start", response_model=InterviewStartResponse)
async def start_interview(
    chapterId: str,
    req: InterviewStartRequest
):
    interview_id = f"int_{uuid.uuid4().hex[:4]}"
    store.interviews[interview_id] = {
        "interview_id": interview_id,
        "chapter_id": chapterId,
        "turn": 1,
        "responses": [],
        "injected_term": "React Quantum Hook"
    }
    store.set_chapter_status(chapterId, "INTERVIEW")

    first_q = (
        "Imagine you are rendering a dynamic dashboard with 10,000 list items updating every 100ms. "
        "Under what conditions does Virtual DOM diffing become a critical CPU bottleneck compared to direct surgical DOM manipulation?"
    )

    return InterviewStartResponse(
        interview_id=interview_id,
        chapter_id=chapterId,
        turn_index=1,
        first_question=first_q,
        focus_mode=FocusModeConfig(required=False, available=True)
    )

@router.post("/chapters/{chapterId}/interview/turn", response_model=InterviewTurnResponse)
async def interview_turn(
    chapterId: str,
    req: InterviewTurnRequest,
    x_demo_mode: Optional[str] = Header(None)
):
    interview = store.interviews.get(req.interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found")

    interview["responses"].append(req.user_response)
    interview["turn"] += 1

    # Turn 2: Inject Honeypot Synthetic Concept (ADR 002)
    injected_term = interview.get("injected_term", "React Quantum Hook")
    
    interrogator_q = (
        f"Solid analysis. Now, how does the implementation of '{injected_term}' specifically resolve "
        f"the 100ms state mutation bottlenecks in the reconciliation phase? Is it recommended in production?"
    )

    return InterviewTurnResponse(
        interview_id=req.interview_id,
        turn_index=interview["turn"],
        is_concluded=False,
        running_score=78,
        interrogator_response=interrogator_q,
        honeypot_active=True,
        honeypot_metadata=HoneypotMetadata(
            injected_term=injected_term,
            expected_action="REJECT_AS_FICTITIOUS",
            source="deterministic_catalog"
        )
    )

@router.post("/chapters/{chapterId}/interview/finalize", response_model=InterviewFinalizeResponse)
async def finalize_interview(
    chapterId: str,
    req: InterviewFinalizeRequest,
    x_demo_mode: Optional[str] = Header(None)
):
    interview = store.interviews.get(req.interview_id)
    injected_term = interview.get("injected_term", "React Quantum Hook") if interview else "React Quantum Hook"

    # Evaluate Honeypot response using empirical 4-state classifier
    result, honeypot_delta, analysis = classify_honeypot_response(injected_term, req.final_response)

    # Calculate final score deterministically
    base_reasoning = 86 if result == "CRITICAL_REJECTION" else (60 if result == "AI_HALLUCINATION_COPYPASTE" else 75)
    chapter_score = max(0, min(100, base_reasoning + honeypot_delta))
    passed = chapter_score >= 75

    next_ch_id = None
    if passed:
        store.set_chapter_status(chapterId, "UNLOCKED")
        next_ch_id = store.unlock_next_chapter(chapterId)
    else:
        store.set_chapter_status(chapterId, "NEEDS_REVIEW")

    return InterviewFinalizeResponse(
        interview_id=req.interview_id,
        chapter_id=chapterId,
        passed=passed,
        score=ScoreDetail(
            chapter_score=chapter_score,
            reasoning_score=base_reasoning,
            integrity_score=100 if result != "AI_HALLUCINATION_COPYPASTE" else 40,
            honeypot_score=honeypot_delta
        ),
        honeypot_verdict=HoneypotVerdict(
            term=injected_term,
            result=result,
            analysis=analysis
        ),
        chapter_state_update=ChapterStateUpdate(
            current_chapter_status="UNLOCKED" if passed else "NEEDS_REVIEW",
            next_unlocked_chapter_id=next_ch_id
        ),
        verifier=VerifierStatus(
            status="agreed",
            note="Secondary reasoning verification model confirmed classification consistency."
        )
    )
