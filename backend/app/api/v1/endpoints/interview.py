"""F9/F10/F13 — Interview quiz, honeypot, and score persistence.

Contract under test: ``POST /api/v1/chapters/:id/interview/{start,turn,finalize}``.

Rules that must hold:
* ``start`` creates an interview, sets ``turn_index = 1`` and moves the chapter to
  ``INTERVIEW``. State is the backend's, not the AI engine's (F9).
* ``turn`` persists the turn history **and** the client telemetry
  (``paste_detected`` / ``duration_seconds`` / ``keystroke_cpm``). That telemetry feeds
  the deterministic pre-filter in ADR 002 s2.1 — never drop it, even when it looks
  unused.
* ``finalize`` scores, writes ``chapter_score``, transitions state, and computes
  ``next_unlocked_chapter_id``. ``>= 75`` -> UNLOCKED, ``< 75`` -> NEEDS_REVIEW (a
  retry, not a dead end).
* Honeypot schema validation is NOT the backend's job: store metadata as received.
* The cached demo path serves a FROZEN verdict, because a recording must not depend on
  how a model or a regex behaves on the day (F17).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query

from ....core import fallback as fb
from ....core import scoring
from ....core.intelligence import telemetry_flag
from ....core.state_machine import (
    InvalidTransition,
    apply_score,
    start_interview_state,
)
from ....repositories import get_store, new_id
from ....schemas import app_addons
from ....schemas.interview import (
    ChapterStateUpdate,
    FocusModeConfig,
    HoneypotMetadata,
    HoneypotVerdict,
    InterviewFinalizeRequest,
    InterviewFinalizeResponse,
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewTurnRequest,
    InterviewTurnResponse,
    ScoreDetail,
    VerifierStatus,
)
from ....services import engine

router = APIRouter()

# Number of rounds before the interviewer concludes (PRD section 4.5: 2-3 rounds).
TOTAL_ROUNDS = 3


def _interview_or_404(interview_id: str) -> Dict[str, Any]:
    interview = get_store().get_interview(interview_id)
    if interview is None:
        raise HTTPException(status_code=404, detail=f"unknown interview: {interview_id}")
    return interview


def _scenario(header_value: Optional[str], scenario: Optional[str]) -> Optional[str]:
    return fb.active_scenario(header_value, scenario)


# ── start ──────────────────────────────────────────────────────────────────────

@router.post("/chapters/{chapterId}/interview/start", response_model=InterviewStartResponse)
async def start_interview(
    chapterId: str,
    req: InterviewStartRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> InterviewStartResponse:
    st = get_store()
    chapter = st.get_chapter(chapterId)
    if chapter is None and (not st.chapters or "ch_algo_01" not in st.chapters):
        from ....core.seeder import seed_store
        seed_store(st)
        chapter = st.get_chapter(chapterId)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapterId}")

    # The gate is enforced at the API, not only in the UI: a LOCKED chapter has no
    # interview (F6). NEEDS_REVIEW is allowed through — that is the retry path.
    try:
        start_interview_state(chapterId)
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    active = _scenario(x_demo_mode, scenario)
    if active:
        if active == "success" and (chapterId.startswith("ch_algo_") or any(k in chapter.get("title", "").lower() for k in ["git", "version", "algo", "complexity", "big-o", "binary", "staging", "commit"])):
            active = "algo_success"
        elif active == "success" and any(k in chapter.get("title", "").lower() for k in ["neyman", "statistics", "statistical", "causal", "likelihood"]):
            active = "stats_success"
        block = fb.cached_interview(active)
        first_question = block["first_question"]
        running_score = int(block.get("running_score", 0))
    else:
        started = engine.engine.start_interview(chapter)
        first_question = started["first_question"]
        running_score = 0

    interview_id = new_id("int", 4)
    scene_data = fb.load_scenario(active) if active else None
    frozen_term = scene_data.get("finalize", {}).get("term") if scene_data else None
    if active and frozen_term:
        injected = {
            "term": frozen_term,
            "catalog_id": f"hp_{active}",
            "category": "Curriculum",
            "source": "deterministic_scenario",
            "expected_action": "REJECT_AS_FICTITIOUS",
        }
    else:
        injected = engine.engine.pick_honeypot_term(
            f"{chapter.get('title', '')} {' '.join(chapter.get('objectives', []) or [])}",
            set(),
            seed=interview_id,
        )
    get_store().create_interview(
        interview_id,
        chapter_id=chapterId,
        session_id=req.session_id,
        turn_index=1,
        running_score=running_score,
        # The term is chosen at start (deterministic, ADR 005) and injected at turn 2.
        injected_term=injected["term"],
        expected_action=injected.get("expected_action", "REJECT_AS_FICTITIOUS"),
        catalog_source=injected.get("source", "deterministic_catalog"),
    )
    get_store().update_chapter(chapterId, interview_id=interview_id)

    return InterviewStartResponse(
        interview_id=interview_id,
        chapter_id=chapterId,
        # Echo the chapter title so the UI header cannot disagree with the question it
        # is showing. Without this the frontend falls back to a per-track hardcoded
        # title, which is how a Virtual DOM question ended up under a Neyman–Pearson
        # heading.
        chapter_title=chapter.get("title"),
        turn_index=1,
        first_question=first_question,
        focus_mode=FocusModeConfig(required=False, available=True),
        engine="deterministic_cache" if active else "live",
    )


# ── turn ───────────────────────────────────────────────────────────────────────

@router.post("/chapters/{chapterId}/interview/turn", response_model=InterviewTurnResponse)
async def interview_turn(
    chapterId: str,
    req: InterviewTurnRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> InterviewTurnResponse:
    interview = _interview_or_404(req.interview_id)
    if interview.get("chapter_id") != chapterId:
        raise HTTPException(
            status_code=409,
            detail=f"interview {req.interview_id} belongs to {interview.get('chapter_id')}",
        )
    active = _scenario(x_demo_mode, scenario)

    # Telemetry is a first-class input (ADR 002 s2.1 pre-filter). Persist it verbatim
    # alongside the turn; a later integrity flag depends on it, and on the caught
    # scenario the paste signal is what makes the drop explainable on camera.
    telemetry = req.client_telemetry.model_dump() if req.client_telemetry else None
    turn_index = max(int(req.turn_index), int(interview.get("turn_index", 1))) + 1
    get_store().add_interview_turn(req.interview_id, {
        "turn_index": turn_index - 1,
        "role": "user",
        "text": req.user_response,
        "client_telemetry": telemetry,
    })

    # Honeypot is injected exactly once, on turn 2 (F10). Re-injecting on every turn
    # would read as a bug and would let one term be answered twice.
    injected_term = interview.get("injected_term")
    already_injected = bool(interview.get("honeypot_injected"))
    honeypot_active = bool(injected_term) and not already_injected and turn_index >= 2

    if honeypot_active:
        interrogator = (
            f"Solid. Now, how exactly does '{injected_term}' resolve the bottleneck you "
            f"described — and would you rely on it in a production build?"
        )
        get_store().update_interview(
            req.interview_id,
            honeypot_injected=True,
            honeypot_metadata={
                "injected_term": injected_term,
                "expected_action": interview.get("expected_action", "REJECT_AS_FICTITIOUS"),
                "source": interview.get("catalog_source", "deterministic_catalog"),
            },
        )
    else:
        interrogator = engine.follow_up(interview, req.user_response, telemetry)

    # Running score is a running signal, not the final grade (F13 scores once, at
    # finalize). It only has to be monotone in effort so the UI can show progress.
    words = len((req.user_response or "").split())
    running_score = min(95, 55 + 10 * turn_index + min(15, words // 8))
    is_concluded = turn_index >= TOTAL_ROUNDS

    get_store().update_interview(
        req.interview_id, turn_index=turn_index, running_score=running_score,
        is_concluded=is_concluded,
    )

    metadata = None
    if honeypot_active:
        metadata = HoneypotMetadata(
            injected_term=injected_term,
            expected_action=interview.get("expected_action", "REJECT_AS_FICTITIOUS"),
            source=interview.get("catalog_source", "deterministic_catalog"),
        )

    return InterviewTurnResponse(
        interview_id=req.interview_id,
        turn_index=turn_index,
        is_concluded=is_concluded,
        running_score=running_score,
        interrogator_response=interrogator,
        honeypot_active=honeypot_active,
        honeypot_metadata=metadata,
        engine="deterministic_cache" if active else "live",
    )


# ── finalize ───────────────────────────────────────────────────────────────────

@router.post(
    "/chapters/{chapterId}/interview/finalize", response_model=InterviewFinalizeResponse
)
async def finalize_interview(
    chapterId: str,
    req: InterviewFinalizeRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> InterviewFinalizeResponse:
    interview = _interview_or_404(req.interview_id)
    chapter = get_store().get_chapter(chapterId)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapterId}")

    active = _scenario(x_demo_mode, scenario)
    injected_term = interview.get("injected_term")
    focus_flag = get_store().get_focus_flag(req.interview_id)
    telemetry = [
        t.get("client_telemetry") for t in interview.get("turns", [])
        if t.get("client_telemetry")
    ]
    paste_seen = any(t.get("paste_detected") for t in telemetry)

    if active:
        active = fb.pick_scenario(requested=scenario, final_response=req.final_response)
        # Frozen outcome: the recording must be byte-identical every take.
        frozen = fb.cached_finalize(active)
        result = frozen["result"]
        analysis = frozen["analysis"]
        reasoning_score = int(frozen["reasoning_score"])
        integrity_flag = frozen["integrity_flag"]
        verifier = dict(frozen["verifier"])
        # A cached scenario has its own frozen term: the runner must narrate the same
        # fake concept the video shows, regardless of what the picker chose at start.
        injected_term = frozen.get("term") or injected_term
        # Publish the scenario's focus events so the integrity log has content on camera.
        from ....core.integrity import derive_integrity

        for event in frozen.get("focus_events", []):
            get_store().add_focus_events(req.interview_id, [event])
        derived = derive_integrity(frozen.get("focus_events", []))
        integrity_flag = focus_flag or derived["integrity_flag"]
        get_store().set_focus_flag(req.interview_id, integrity_flag)
    else:
        verdict = engine.engine.classify_honeypot(req.final_response, injected_term) \
            if injected_term else {"result": "NONE", "points": 0,
                                   "analysis": "No honeypot was injected this session."}
        result = verdict["result"]
        analysis = verdict["analysis"]
        # `reasoning_score` goes through the engine when it exposes the capability and
        # falls back deterministically when it does not (services.engine).
        reasoning_score = engine.reasoning_score(req.final_response)
        integrity_flag = telemetry_flag(paste_seen=paste_seen, focus_flag=focus_flag)
        verifier = engine.engine.verify_score(
            {"result": result, "points": verdict.get("points", 0)},
            {"final_response": req.final_response},
        )

    points = engine.engine.CLASS_POINTS.get(result, 0)
    score = scoring.chapter_score(reasoning_score, points, integrity_flag)
    # The verifier loop is binding: an `uncertain` verdict caps the score below the
    # unlock threshold, otherwise risk R3 ("LLM grading LLM") is untested decoration.
    score = scoring.apply_verifier(score, verifier)

    try:
        outcome = apply_score(chapterId, score)
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    get_store().update_chapter(
        chapterId,
        interview_id=req.interview_id,
        integrity_flag=integrity_flag,
        honeypot_verdict={"term": injected_term, "result": result, "analysis": analysis},
        verifier=verifier,
    )
    get_store().update_interview(req.interview_id, finalized=True, final_response=req.final_response)

    return InterviewFinalizeResponse(
        interview_id=req.interview_id,
        chapter_id=chapterId,
        passed=outcome["passed"],
        score=ScoreDetail(**{
            "chapter_score": score["chapter_score"],
            "reasoning_score": score["reasoning_score"],
            "integrity_score": score["integrity_score"],
            "honeypot_score": score["honeypot_score"],
        }),
        honeypot_verdict=HoneypotVerdict(
            term=injected_term, result=result, analysis=analysis
        ),
        chapter_state_update=ChapterStateUpdate(
            current_chapter_status=outcome["status"],
            next_unlocked_chapter_id=outcome["next_unlocked_chapter_id"],
        ),
        verifier=VerifierStatus(status=verifier["status"], note=verifier["note"]),
        fallback=fb.cached_response(active) if active else None,
        integrity_flag=integrity_flag,
        score_explanation=app_addons.explain_score_delta(score, integrity_flag),
        cache=app_addons.cache_meta(fb.CACHE_SCHEMA_VERSION) if active else None,
    )
