"""F15 (appeal) and F16 (final report) — API-CONTRACTS section 2.8.

Two decisions worth stating:

* **The report is an aggregation over real chapter documents, not a fixture.** The earlier
  stub returned two hard-coded chapters with scores 88 and 62. That survives exactly until
  the first demo takes a different path, and then the numbers on screen contradict the
  chapters the audience just watched — the most damaging failure mode for a report page.
* **``mean_calibration_gap`` averages ``abs()``.** The per-chapter gap is signed so the UI
  can say "overconfident", but averaging signed gaps lets +28 and -28 cancel into a fake
  "well calibrated". The contract's example (mean 15 from gaps 2 and 28) only works with
  absolute values (see ``app_addons.calibration_labels`` for the same trap).
"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query

from ....core import fallback as fb
from ....repositories import get_store
from ....schemas import app_addons
from ....schemas.report import (
    CONTRACT_APPEAL_OUTCOMES,
    ENGINE_APPEAL_OUTCOMES,
    AppealRequest,
    AppealResponse,
    ChapterReportItem,
    FinalReportResponse,
    ReportSummary,
)

router = APIRouter()


def _honeypot_counts(chapters) -> dict:
    """Verdict class -> count, over chapters that actually had an injected term.

    ``NONE`` is excluded: counting it would put a phantom row in the report's legend for
    every chapter where the honeypot was never reached.
    """
    counts: dict = {}
    for chapter in chapters:
        verdict = chapter.get("honeypot_verdict") or {}
        result = verdict.get("result")
        if result and result != "NONE":
            counts[result] = counts.get(result, 0) + 1
    return counts


def _syllabus_title(session, chapters) -> str:
    title = (session or {}).get("syllabus_title")
    if title:
        return str(title)
    role = (session or {}).get("role") or "Study"
    return f"{role} Deep Dive"


def _build_chapters(chapters) -> list:
    items = []
    for chapter in chapters:
        score = chapter.get("score") or {}
        calibration = chapter.get("calibration") or {}
        items.append(ChapterReportItem(
            chapter_id=chapter["chapter_id"],
            title=chapter.get("title"),
            status=chapter.get("status", "LOCKED"),
            # An unscored chapter reports 0 and its status says why. Inventing a number
            # would be indistinguishable from a real low score on camera.
            score=int(score.get("chapter_score", 0)),
            calibration_gap=calibration.get("calibration_gap"),
            integrity=chapter.get("integrity_flag", "clean"),
            honeypot_result=(chapter.get("honeypot_verdict") or {}).get("result"),
            focus_summary=chapter.get("focus_summary"),
        ))
    return items


@router.get("/report/{sessionId}", response_model=FinalReportResponse)
async def get_final_report(
    sessionId: str,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> FinalReportResponse:
    session = get_store().get_session(sessionId)
    if session is None:
        raise HTTPException(status_code=404, detail=f"unknown session: {sessionId}")

    chapters = get_store().session_chapters(sessionId)
    items = _build_chapters(chapters)

    # Honest aggregation: no scored chapters means 0.0 — not a division by zero, and not a
    # flattering default that would make an abandoned session look complete.
    scored = [c for c in items if c.score > 0]
    mean_score = round(sum(c.score for c in scored) / len(scored), 2) if scored else 0.0

    gaps = [c.calibration_gap for c in items if c.calibration_gap is not None]
    mean_gap = round(sum(abs(g) for g in gaps) / len(gaps), 2) if gaps else 0.0

    summary = ReportSummary(
        mean_score=mean_score,
        mean_calibration_gap=mean_gap,
        integrity_flags=sum(1 for c in items if c.integrity != "clean"),
        honeypot_verdicts=_honeypot_counts(chapters),
    )

    integrity_log = [
        {
            "chapter_id": c.chapter_id,
            "integrity": c.integrity,
            "focus_summary": c.focus_summary,
        }
        for c in items
        if c.integrity != "clean" or c.focus_summary
    ]

    active = fb.active_scenario(x_demo_mode, scenario)
    calibration = []
    for item, chapter in zip(items, chapters):
        stored = chapter.get("calibration") or {}
        calibration.append({
            "chapter_id": item.chapter_id,
            "predicted_score": stored.get("predicted_score"),
            "actual_score": item.score,
            "calibration_gap": item.calibration_gap,
            "label": stored.get("label"),
        })

    return FinalReportResponse(
        session_id=sessionId,
        syllabus_title=_syllabus_title(session, chapters),
        chapters=items,
        summary=summary,
        calibration=calibration,
        integrity_log=integrity_log,
        cache=app_addons.cache_meta(fb.CACHE_SCHEMA_VERSION) if active else None,
    )


@router.post("/chapters/{chapterId}/appeal", response_model=AppealResponse)
async def appeal_score(
    chapterId: str,
    req: AppealRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> AppealResponse:
    """Route an appeal to the verifier; never auto-resolve (WBS section 7, cut #1).

    Held to stub depth on purpose. The endpoint still writes a real row and returns the
    contract's shape, so the frontend can wire against it today; the reviewer behind it is
    a person, not a model that flips the score on the spot.
    """
    chapter = get_store().get_chapter(chapterId)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapterId}")

    active = fb.active_scenario(x_demo_mode, scenario)
    appeal_id = f"apl_{uuid.uuid4().hex[:4]}"
    engine_outcome = list(ENGINE_APPEAL_OUTCOMES)

    try:
        from ....services import engine

        routed = engine.engine.appeal(chapterId, req.reason)
        engine_outcome = list(routed.get("possible_outcome", ENGINE_APPEAL_OUTCOMES))
        appeal_id = routed.get("appeal_id", appeal_id)
    except Exception:
        # The appeal is a stub by design: if the engine cannot be reached the request is
        # still accepted and queued. A 500 here would remove a student's only recourse.
        pass

    get_store().save_appeal(appeal_id, {
        "chapter_id": chapterId,
        "interview_id": req.interview_id,
        "reason": req.reason,
        "status": "under_review",
        "reviewer": "verifier_model",
    })

    return AppealResponse(
        appeal_id=appeal_id,
        status="under_review",
        reviewer="verifier_model",
        # The contract's vocabulary, not the engine's. DEV 3's tokens are reported in a
        # separate field so its naming stays visible without leaking two vocabularies into
        # the same UI field.
        possible_outcome=list(CONTRACT_APPEAL_OUTCOMES),
        chapter_id=chapterId,
        engine_outcome=engine_outcome,
    )
