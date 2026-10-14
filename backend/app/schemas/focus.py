from typing import List, Literal, Optional
from pydantic import BaseModel

FocusEventType = Literal["GAZE_DRIFT", "MULTIPLE_FACES", "TAB_BLUR", "CAMERA_OFF"]

class FocusEventItem(BaseModel):
    type: FocusEventType
    at_ms: int
    duration_ms: Optional[int] = None
    count: Optional[int] = None

class FocusEventsRequest(BaseModel):
    interview_id: str
    events: List[FocusEventItem]
    video_transmitted: bool = False  # MUST BE FALSE for privacy (ADR 003)

class FocusSummary(BaseModel):
    gaze_drift_count: int = 0
    multi_face_count: int = 0
    tab_blur_count: int = 0

class FocusEventsResponse(BaseModel):
    integrity_flag: str  # "clean", "assisted", or "assisted_unverified"
    auto_blur: bool
    summary: FocusSummary
