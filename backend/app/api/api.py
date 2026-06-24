from fastapi import APIRouter
from app.api import auth, user, institution, attendance, notification, academic, device, sms

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(institution.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(notification.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(device.router, prefix="/device", tags=["device"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
