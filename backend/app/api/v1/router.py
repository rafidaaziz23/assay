from fastapi import APIRouter
from .endpoints import (
    intake,
    chapters,
    interview,
    calibration,
    focus,
    report,
    auth,
    dashboard,
    settings,
    notifications,
)

api_router = APIRouter()

api_router.include_router(auth.router, tags=["Authentication & Profile"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(notifications.router, tags=["Notifications & Alerts"])
api_router.include_router(intake.router, tags=["Intake & Syllabus"])
api_router.include_router(chapters.router, tags=["Chapter Reader & Socratic Ask"])
api_router.include_router(interview.router, tags=["Interview & Honeypot"])
api_router.include_router(calibration.router, tags=["Calibration"])
api_router.include_router(focus.router, tags=["Focus Mode"])
api_router.include_router(report.router, tags=["Report & Appeal"])
api_router.include_router(settings.router, tags=["Settings"])
