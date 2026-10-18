"""F9/F13 — Interview quiz, honeypot, and score schemas (API-CONTRACTS section 2.5)."""
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field

HoneypotResult = Literal[
    "CRITICAL_REJECTION",
    "AI_HALLUCINATION_COPYPASTE",
    "UNVERIFIED_HONEST",
    "EVASIVE",
    "NONE",
]


class FocusModeConfig(BaseModel):
    required: bool = False
    available: bool = True


class InterviewStartRequest(BaseModel):
    session_id: str


class InterviewStartResponse(BaseModel):
    interview_id: str
    chapter_id: str
    chapter_title: Optional[str] = None
    turn_index: int = 1
    first_question: str
    focus_mode: FocusModeConfig = FocusModeConfig()
    engine: Optional[str] = None


class ClientTelemetry(BaseModel):
    """Deterministic pre-filter input (ADR 002 s2.1).

    Never drop these even when they look unused: ``paste_detected`` and
    ``keystroke_cpm`` are what separate a typed answer from a pasted one, and that
    distinction feeds the integrity flag on the caught scenario.
    """

    paste_detected: bool = False
    duration_seconds: int = 0
    keystroke_cpm: int = 0


class InterviewTurnRequest(BaseModel):
    interview_id: str
    turn_index: int
    user_response: str
    client_telemetry: Optional[ClientTelemetry] = None


class HoneypotMetadata(BaseModel):
    injected_term: str
    expected_action: str
    source: str = "deterministic_catalog"


class InterviewTurnResponse(BaseModel):
    interview_id: str
    turn_index: int
    is_concluded: bool = False
    running_score: int = 0
    interrogator_response: str
    honeypot_active: bool = False
    honeypot_metadata: Optional[HoneypotMetadata] = None
    engine: Optional[str] = None


class InterviewFinalizeRequest(BaseModel):
    interview_id: str
    final_response: str = Field(..., min_length=1)


class ScoreDetail(BaseModel):
    chapter_score: int
    reasoning_score: int
    integrity_score: int
    honeypot_score: int


class HoneypotVerdict(BaseModel):
    term: Optional[str] = None
    result: HoneypotResult = "NONE"
    analysis: str = ""


class ChapterStateUpdate(BaseModel):
    current_chapter_status: str
    next_unlocked_chapter_id: Optional[str] = None


class VerifierStatus(BaseModel):
    status: str
    note: str


class InterviewFinalizeResponse(BaseModel):
    interview_id: str
    chapter_id: str
    passed: bool
    score: ScoreDetail
    honeypot_verdict: HoneypotVerdict
    chapter_state_update: ChapterStateUpdate
    verifier: VerifierStatus
    # DEV 2 additions: `fallback` carries the cached-scenario envelope when DEMO_MODE
    # is cached; `score_explanation` breaks the total into its named parts so the
    # "caught" beat is explainable on camera (app_addons.explain_score_delta).
    fallback: Optional[dict[str, Any]] = None
    integrity_flag: Optional[str] = None
    score_explanation: Optional[dict[str, Any]] = None
    cache: Optional[dict[str, Any]] = None
