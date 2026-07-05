from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.notification import NotificationLog
from app.models.device import Device
from app.models.user import User
from app.api.deps import get_current_management_or_faculty
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class NotificationLogResponse(BaseModel):
    id: int
    channel: str
    recipient: str
    status: str
    message: str
    provider_response: Optional[str]
    created_at: datetime
    device_name: Optional[str] = None

    class Config:
        orm_mode = True

@router.get("/logs", response_model=List[NotificationLogResponse])
def get_notification_logs(
    limit: int = 100, 
    offset: int = 0,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_management_or_faculty)
):
    """ Fetch immutable audit logs for notifications. """
    logs = db.query(NotificationLog).filter(
        NotificationLog.tenant_id == current_user.tenant_id
    ).order_by(NotificationLog.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    # Pre-fetch devices for mapping
    device_ids = [l.device_id for l in logs if l.device_id]
    devices = {}
    if device_ids:
        devs = db.query(Device).filter(Device.id.in_(device_ids)).all()
        devices = {d.id: d.device_name for d in devs}
        
    for log in logs:
        result.append({
            "id": log.id,
            "channel": log.channel,
            "recipient": log.recipient,
            "status": log.status,
            "message": log.message,
            "provider_response": log.provider_response,
            "created_at": log.created_at,
            "device_name": devices.get(log.device_id) if log.device_id else None
        })
    return result
