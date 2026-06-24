from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.sms import SmsQueue
from app.models.device import Device
from app.models.notification import NotificationLog
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class SmsPendingResponse(BaseModel):
    id: int
    recipient_name: Optional[str]
    recipient_phone: str
    message: str

    class Config:
        orm_mode = True

class SmsStatusUpdateRequest(BaseModel):
    device_uuid: str
    sms_id: int
    status: str # "SENT", "FAILED", "DELIVERED"
    error_message: Optional[str] = None


@router.get("/pending", response_model=List[SmsPendingResponse])
def get_pending_sms(device_uuid: str, db: Session = Depends(get_db)):
    # Authenticate device
    device = db.query(Device).filter(Device.device_uuid == device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    # Get pending SMS for this tenant
    # Sort by priority (1 is highest) and then by oldest first
    pending = db.query(SmsQueue).filter(
        SmsQueue.tenant_id == device.tenant_id,
        SmsQueue.status == "PENDING"
    ).order_by(SmsQueue.priority.asc(), SmsQueue.created_at.asc()).limit(50).all()
    
    # Mark them as processing so other devices don't pick them up
    for sms in pending:
        sms.status = "PROCESSING"
    db.commit()
    
    return pending

@router.post("/status")
def update_sms_status(request: SmsStatusUpdateRequest, db: Session = Depends(get_db)):
    # Authenticate device
    device = db.query(Device).filter(Device.device_uuid == request.device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    sms = db.query(SmsQueue).filter(
        SmsQueue.id == request.sms_id,
        SmsQueue.tenant_id == device.tenant_id
    ).first()
    
    if not sms:
        raise HTTPException(status_code=404, detail="SMS not found")
        
    sms.status = request.status
    
    # Update the corresponding NotificationLog
    log = db.query(NotificationLog).filter(
        NotificationLog.tenant_id == sms.tenant_id,
        NotificationLog.channel == "SMS",
        NotificationLog.recipient == sms.recipient_phone,
        NotificationLog.status.in_(["PENDING", "PROCESSING"])
    ).first()
    
    if log:
        log.status = request.status
        log.provider_response = request.error_message or f"Status updated by {device.device_name}"
        
    db.commit()
    
    return {"status": "ok"}
