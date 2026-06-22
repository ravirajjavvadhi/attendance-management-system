from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.notification import NotificationLog
from app.models.user import User
from app.api.deps import get_current_admin
from pydantic import BaseModel

router = APIRouter()

class SMSPendingResponse(BaseModel):
    id: int
    mobile_number: str
    content: str

class SMSStatusUpdate(BaseModel):
    status: str
    error_message: str = None

@router.get("/sms/pending", response_model=List[SMSPendingResponse])
def get_pending_sms(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """ Endpoint for Android Device to fetch pending SMS to send. """
    logs = db.query(NotificationLog).filter(
        NotificationLog.tenant_id == current_admin.tenant_id,
        NotificationLog.type == "SMS",
        NotificationLog.status == "PENDING"
    ).limit(50).all()
    
    result = []
    for log in logs:
        # Find mobile number
        user = db.query(User).filter(User.id == log.user_id).first()
        from app.models.profiles import StudentProfile
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        
        if profile and profile.parent_mobile:
            result.append({
                "id": log.id,
                "mobile_number": profile.parent_mobile,
                "content": log.content
            })
    return result

@router.put("/sms/{log_id}/status")
def update_sms_status(log_id: int, status_update: SMSStatusUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    """ Endpoint for Android Device to update delivery status. """
    log = db.query(NotificationLog).filter(
        NotificationLog.id == log_id,
        NotificationLog.tenant_id == current_admin.tenant_id
    ).first()
    
    if log:
        log.status = status_update.status
        log.error_message = status_update.error_message
        db.commit()
        return {"message": "Status updated"}
    return {"message": "Log not found"}
