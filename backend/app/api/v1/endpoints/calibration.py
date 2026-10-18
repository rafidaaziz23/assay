"""F14 — Calibration endpoint (API-CONTRACTS section 2.6).

The upstream stub answered with a hard-coded ``actual_score = 88``. That is not a
calibration: it is a screenshot. The actual score is read from the chapter's stored score,
so the number on screen is the number the student actually earned.

``predicted_score`` is taken BEFORE the reveal by definition, so it is persisted (one row
per chapter, latest wins) — the report needs the predicted value to render the
predicted-vs-actual table.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Query

from ....core import fallback as fb
from ....repositories import get_store
from ....schemas.app_addons import calibration_labels
from ....schemas.calibration import CalibrationRequest, CalibrationResponse

router = APIRouter()


def _actual_score(chapter: dict) -> Optional[int]:
    """The chapter's real score. ``None`` when the chapter has not been scored yet."""
    if not chapter:
        return None
    score = chapter.get("score") or {}
    value = score.get("chapter_score")
    return int(value) if value is not None else None


@router.post("/chapters/{chapterId}/calibration", response_model=CalibrationResponse)
async def submit_calibration(
    chapterId: str,
    req: CalibrationRequest,
    x_demo_mode: Optional[str] = Header(None),
    scenario: Optional[str] = Query(None),
) -> CalibrationResponse:
    chapter = get_store().get_chapter(chapterId)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"unknown chapter: {chapterId}")

    actual = _actual_score(chapter)
    if actual is None:
        # 409, not a 200 with a guessed number: predicting a score that does not exist yet
        # is a caller sequencing error (PRD section 3 Step 6 puts calibration before the
        # reveal but after the interview produced a score).
        raise HTTPException(
            status_code=409,
            detail=f"chapter {chapterId} has no score yet; finalize the interview first",
        )

    active = fb.active_scenario(x_demo_mode, scenario)
    if active:
        result = fb.cached_calibration(req.predicted_score, actual, active)
    else:
        gap, label = calibration_labels(req.predicted_score - actual)
        result = {
            "predicted_score": req.predicted_score,
            "actual_score": actual,
            "calibration_gap": gap,
            "label": label,
        }

    get_store().save_calibration(chapterId, dict(result, interview_id=req.interview_id))

    return CalibrationResponse(
        **result,
        interview_id=req.interview_id,
        fallback=fb.cached_response(active) if active else None,
    )
