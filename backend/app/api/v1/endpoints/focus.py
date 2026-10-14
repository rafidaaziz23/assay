from fastapi import APIRouter
from ....schemas.focus import FocusEventsRequest, FocusEventsResponse, FocusSummary
from ....core.state_machine import store

router = APIRouter()

@router.post("/chapters/{chapterId}/focus-events", response_model=FocusEventsResponse)
async def record_focus_events(
    chapterId: str,
    req: FocusEventsRequest
):
    # Store events in session
    if req.interview_id not in store.focus_events:
        store.focus_events[req.interview_id] = []
    store.focus_events[req.interview_id].extend(req.events)

    gaze_count = sum(1 for e in req.events if e.type == "GAZE_DRIFT")
    face_count = sum(1 for e in req.events if e.type == "MULTIPLE_FACES")
    blur_count = sum(1 for e in req.events if e.type == "TAB_BLUR")

    has_suspicion = gaze_count > 0 or face_count > 0 or blur_count > 0
    flag = "assisted" if has_suspicion else "clean"

    return FocusEventsResponse(
        integrity_flag=flag,
        auto_blur=has_suspicion,
        summary=FocusSummary(
            gaze_drift_count=gaze_count,
            multi_face_count=face_count,
            tab_blur_count=blur_count
        )
    )
