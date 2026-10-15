"""F14 — Calibration schemas (API-CONTRACTS section 2.6)."""
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

CalibrationLabel = Literal["well_calibrated", "overconfident", "underconfident"]


class CalibrationRequest(BaseModel):
    interview_id: str
    # 0-100, sent BEFORE the score is revealed (PRD section 3 Step 6).
    predicted_score: int = Field(..., ge=0, le=100)


class CalibrationResponse(BaseModel):
    predicted_score: int
    actual_score: int
    # Signed difference (predicted - actual). The contract shows 90 vs 88 -> gap 2, and
    # a negative gap is what makes `underconfident` meaningful; see
    # app_addons.calibration_labels for why the report averages abs() instead.
    calibration_gap: int
    label: CalibrationLabel
    interview_id: Optional[str] = None
    fallback: Optional[dict[str, Any]] = None
