from fastapi import APIRouter
from .endpoints import intake, chapters, interview, calibration, focus, report

api_router = APIRouter()

api_router.include_router(intake.router, tags=["Intake & Syllabus"])
api_router.include_router(chapters.router, tags=["Chapter Reader & Socratic Ask"])
api_router.include_router(interview.router, tags=["Interview & Honeypot"])
api_router.include_router(calibration.router, tags=["Calibration"])
api_router.include_router(focus.router, tags=["Focus Mode"])
api_router.include_router(report.router, tags=["Report & Appeal"])
