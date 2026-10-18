"""F11/F12 — Focus Mode event schemas (API-CONTRACTS section 2.7, ADR 003)."""
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator

FocusEventType = Literal["GAZE_DRIFT", "MULTIPLE_FACES", "TAB_BLUR", "CAMERA_OFF"]
IntegrityFlag = Literal["clean", "assisted", "assisted_unverified"]


class FocusEventItem(BaseModel):
    # extra="forbid" on purpose (ADR 003 s2.2). Pydantic's default silently DROPS unknown
    # keys, so a client sending `frame: "<base64>"` would receive a cheerful 200 while the
    # server quietly discarded the blob — the privacy invariant would hold by accident and
    # nobody would know a client was trying to send video. Forbidding extra keys makes the
    # violation visible as a 422 instead of a silent no-op.
    model_config = ConfigDict(extra="forbid")

    type: FocusEventType
    at_ms: int
    duration_ms: Optional[int] = None
    count: Optional[int] = None


class FocusEventsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interview_id: str
    events: List[FocusEventItem] = []
    # Privacy invariant (ADR 003 s2.2): on-device inference only, boolean events to the
    # server. The contract freezes this field as false; a true value is rejected here so
    # no handler can accidentally accept video.
    video_transmitted: bool = False
    # Accessible Mode (camera off) is a first-class path, not an error (F11/F12).
    accessible_mode: bool = False

    @model_validator(mode="after")
    def reject_video(self) -> "FocusEventsRequest":
        if self.video_transmitted:
            raise ValueError("video_transmitted must be false (ADR 003)")
        return self


class FocusSummary(BaseModel):
    gaze_drift_count: int = 0
    multi_face_count: int = 0
    tab_blur_count: int = 0


class FocusEventsResponse(BaseModel):
    integrity_flag: IntegrityFlag
    auto_blur: bool
    summary: FocusSummary
    # DEV 2 additions: `integrity_score` no longer needs guessing, and the report needs
    # the per-chapter focus summary (F16).
    integrity_score: Optional[int] = None
    accessible_mode: Optional[bool] = None
    fallback: Optional[dict[str, Any]] = None
