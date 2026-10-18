"""F15/F16 — Appeal and final report schemas (API-CONTRACTS section 2.8)."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Frozen compatibility: the frontend and the contract both use these three tokens.
# ai/appeal() returns ("upheld", "score_revised", "re_interview") — DEV 3's naming.
# The backend is the one that talks to the client, so it normalises to the contract's
# vocabulary rather than shipping two different vocabularies to the same screen.
AppealOutcome = str
CONTRACT_APPEAL_OUTCOMES = ["upheld", "revised", "uncertain"]
ENGINE_APPEAL_OUTCOMES = ["upheld", "score_revised", "re_interview"]


class AppealRequest(BaseModel):
    interview_id: str
    reason: str


class AppealResponse(BaseModel):
    appeal_id: str
    status: str
    reviewer: str
    possible_outcome: List[AppealOutcome]
    chapter_id: Optional[str] = None
    engine_outcome: Optional[List[str]] = None


class ChapterReportItem(BaseModel):
    chapter_id: str
    title: Optional[str] = None
    status: str
    score: int
    # Per-chapter gap kept SIGNED to match API-CONTRACTS section 2.8's example
    # (ch_02 shows +28 = overconfident). The summary below averages abs() so
    # +28 and -28 cannot cancel into a fake "well calibrated" (app_addons).
    calibration_gap: Optional[int] = None
    integrity: str
    honeypot_result: Optional[str] = None
    focus_summary: Optional[Dict[str, Any]] = None


class ReportSummary(BaseModel):
    mean_score: float
    mean_calibration_gap: float
    integrity_flags: int
    honeypot_verdicts: Dict[str, int]


class FinalReportResponse(BaseModel):
    session_id: str
    syllabus_title: str
    chapters: List[ChapterReportItem]
    summary: ReportSummary
    # DEV 2 additions: `calibration` shows predicted vs actual per chapter (the slider
    # moment is a rubric item) and `cache` carries the fallback envelope.
    calibration: Optional[List[Dict[str, Any]]] = None
    integrity_log: Optional[List[Dict[str, Any]]] = None
    cache: Optional[Dict[str, Any]] = None
