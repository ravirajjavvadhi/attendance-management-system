from fastapi import APIRouter
from app.api import auth, user, institution, attendance, notification, academic, device, sms, timetable

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(institution.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(notification.router, prefix="/legacy-notifications", tags=["legacy-notifications"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(timetable.router, prefix="/academic/timetable", tags=["timetable"])
api_router.include_router(device.router, prefix="/device", tags=["device"])
api_router.include_router(device.router, prefix="/devices", tags=["device"])
api_router.include_router(sms.router, prefix="/legacy-sms", tags=["legacy-sms"])

# New API Gateway Consumer Routers
from app.api.consumers import admin, management, faculty, parent, student, analytics, reports, sms_gateway, notifications_engine

api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(management.router, prefix="/management", tags=["management"])
api_router.include_router(faculty.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(parent.router, prefix="/parent", tags=["parent"])
api_router.include_router(student.router, prefix="/student", tags=["student"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications_engine.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(sms_gateway.router, prefix="/sms", tags=["sms"])
