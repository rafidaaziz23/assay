from typing import List, Optional, Literal
from pydantic import BaseModel

HoneypotResult = Literal[
    "CRITICAL_REJECTION",
    "AI_HALLUCINATION_COPYPASTE",
    "UNVERIFIED_HONEST",
    "EVASIVE",
    "NONE"
]

class FocusModeConfig(BaseModel):
    required: bool = False
    available: bool = True

class InterviewStartRequest(BaseModel):
    session_id: str

class InterviewStartResponse(BaseModel):
    interview_id: str
    chapter_id: str
    turn_index: int = 1
    first_question: str
    focus_mode: FocusModeConfig = FocusModeConfig()

class ClientTelemetry(BaseModel):
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

class InterviewFinalizeRequest(BaseModel):
    interview_id: str
    final_response: str

class ScoreDetail(BaseModel):
    chapter_score: int
    reasoning_score: int
    integrity_score: int
    honeypot_score: int

class HoneypotVerdict(BaseModel):
    term: str
    result: HoneypotResult
    analysis: str

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
