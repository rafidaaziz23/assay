from typing import Literal
from pydantic import BaseModel, Field

CalibrationLabel = Literal["well_calibrated", "overconfident", "underconfident"]

class CalibrationRequest(BaseModel):
    interview_id: str
    predicted_score: int = Field(..., ge=0, le=100)

class CalibrationResponse(BaseModel):
    predicted_score: int
    actual_score: int
    calibration_gap: int
    label: CalibrationLabel
