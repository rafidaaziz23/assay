from fastapi import APIRouter
from ....schemas.calibration import CalibrationRequest, CalibrationResponse

router = APIRouter()

@router.post("/chapters/{chapterId}/calibration", response_model=CalibrationResponse)
async def submit_calibration(
    chapterId: str,
    req: CalibrationRequest
):
    # Fixed reference actual score for calibration curve demo
    actual_score = 88
    gap = abs(req.predicted_score - actual_score)

    if req.predicted_score > actual_score + 15:
        label = "overconfident"
    elif req.predicted_score < actual_score - 15:
        label = "underconfident"
    else:
        label = "well_calibrated"

    return CalibrationResponse(
        predicted_score=req.predicted_score,
        actual_score=actual_score,
        calibration_gap=gap,
        label=label
    )
