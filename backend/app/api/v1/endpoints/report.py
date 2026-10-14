import uuid
from fastapi import APIRouter
from ....schemas.report import (
    FinalReportResponse,
    ChapterReportItem,
    ReportSummary,
    AppealRequest,
    AppealResponse
)
from ....core.state_machine import store

router = APIRouter()

@router.get("/report/{sessionId}", response_model=FinalReportResponse)
async def get_final_report(sessionId: str):
    session = store.get_session(sessionId)
    title = "Frontend Deep Dive: React Internals"
    
    chapters_report = [
        ChapterReportItem(
            chapter_id="ch_01",
            status="UNLOCKED",
            score=88,
            calibration_gap=2,
            integrity="clean"
        ),
        ChapterReportItem(
            chapter_id="ch_02",
            status="NEEDS_REVIEW",
            score=62,
            calibration_gap=28,
            integrity="assisted"
        )
    ]

    return FinalReportResponse(
        session_id=sessionId,
        syllabus_title=title,
        chapters=chapters_report,
        summary=ReportSummary(
            mean_score=75.0,
            mean_calibration_gap=15.0,
            integrity_flags=1,
            honeypot_verdicts={
                "CRITICAL_REJECTION": 1,
                "UNVERIFIED_HONEST": 1
            }
        )
    )

@router.post("/chapters/{chapterId}/appeal", response_model=AppealResponse)
async def appeal_score(chapterId: str, req: AppealRequest):
    appeal_id = f"apl_{uuid.uuid4().hex[:4]}"
    store.appeals[appeal_id] = {
        "chapter_id": chapterId,
        "interview_id": req.interview_id,
        "reason": req.reason,
        "status": "under_review"
    }
    return AppealResponse(
        appeal_id=appeal_id,
        status="under_review",
        reviewer="verifier_model",
        possible_outcome=["upheld", "revised", "uncertain"]
    )
