from typing import List, Dict, Optional, Literal
from pydantic import BaseModel

AppealOutcome = Literal["upheld", "revised", "uncertain"]

class AppealRequest(BaseModel):
    interview_id: str
    reason: str

class AppealResponse(BaseModel):
    appeal_id: str
    status: str
    reviewer: str
    possible_outcome: List[AppealOutcome]

class ChapterReportItem(BaseModel):
    chapter_id: str
    status: str
    score: int
    calibration_gap: int
    integrity: str

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
