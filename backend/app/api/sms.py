from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.sms import SmsQueue
from app.models.device import Device
from app.models.notification import NotificationLog
from app.models.tenant import Institution
from app.models.user import User
from app.api.deps import get_current_management_or_faculty
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

router = APIRouter()

class SmsPendingResponse(BaseModel):
    id: int
    message_uuid: Optional[str] = None
    recipient_name: Optional[str]
    recipient_phone: str
    message: str

    class Config:
        orm_mode = True

class SmsAckRequest(BaseModel):
    device_uuid: str
    message_uuids: List[str]

class SmsStatusUpdateRequest(BaseModel):
    device_uuid: str
    sms_id: Optional[int] = None
    message_uuid: Optional[str] = None
    status: str # "SENT", "FAILED", "DELIVERED", "SENDING"
    error_message: Optional[str] = None

@router.get("/pending", response_model=List[SmsPendingResponse])
def get_pending_sms(device_uuid: str, limit: int = 50, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uuid == device_uuid, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    institution = db.query(Institution).filter(Institution.id == device.tenant_id).first()
    engine = getattr(institution, "sms_engine", "LEGACY")
    max_quota = getattr(institution, "max_sms_per_device_per_day", 70)
    
    today_utc = datetime.now(timezone.utc).date()
    
    if engine == "ENTERPRISE":
        # 1. Recover un-ACKed CLAIMED jobs (> 60 secs)
        stale_threshold = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.query(SmsQueue).filter(
            SmsQueue.tenant_id == device.tenant_id,
            SmsQueue.status == "CLAIMED",
            SmsQueue.processing_started_at < stale_threshold
        ).update({"status": "PENDING", "processed_by_device_id": None, "processing_started_at": None})
        
        # 2. Recover SENDING/READY_TO_SEND that got stuck for > 90 secs
        stale_send_threshold = datetime.now(timezone.utc) - timedelta(seconds=90)
        db.query(SmsQueue).filter(
            SmsQueue.tenant_id == device.tenant_id,
            SmsQueue.status.in_(["READY_TO_SEND", "SENDING"]),
            SmsQueue.processing_started_at < stale_send_threshold
        ).update({"status": "PENDING", "processed_by_device_id": None, "processing_started_at": None})
        db.commit()
        
        # Check quota
        daily_usage = db.query(func.count(SmsQueue.id)).filter(
            SmsQueue.processed_by_device_id == device.id,
            func.date(SmsQueue.processing_started_at) == today_utc
        ).scalar() or 0
        
        remaining_quota = max(0, max_quota - daily_usage)
        if remaining_quota <= 0:
            return []
            
        batch_limit = min(limit, remaining_quota)
        
        # Atomic lock
        pending = db.query(SmsQueue).filter(
            SmsQueue.tenant_id == device.tenant_id,
            SmsQueue.status == "PENDING"
        ).order_by(
            SmsQueue.priority.asc(), 
            SmsQueue.created_at.asc()
        ).limit(batch_limit).with_for_update(skip_locked=True).all()
        
        for sms in pending:
            sms.status = "CLAIMED"
            sms.processed_by_device_id = device.id
            sms.processing_started_at = func.now()
        
        db.commit()
        return pending
    
    else:
        # LEGACY MODE
        stale_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
        db.query(SmsQueue).filter(
            SmsQueue.tenant_id == device.tenant_id,
            SmsQueue.status == "IN_PROGRESS",
            SmsQueue.processing_started_at < stale_threshold
        ).update({"status": "PENDING", "processing_started_at": None})
        db.commit()
        
        pending = db.query(SmsQueue).filter(
            SmsQueue.tenant_id == device.tenant_id,
            SmsQueue.status == "PENDING"
        ).order_by(SmsQueue.priority.asc(), SmsQueue.created_at.asc()).limit(limit).all()
        
        for sms in pending:
            sms.status = "IN_PROGRESS"
            sms.processing_started_at = func.now()
        db.commit()
        return pending


@router.post("/ack")
def ack_sms(request: SmsAckRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uuid == request.device_uuid, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    db.query(SmsQueue).filter(
        SmsQueue.tenant_id == device.tenant_id,
        SmsQueue.processed_by_device_id == device.id,
        SmsQueue.message_uuid.in_(request.message_uuids),
        SmsQueue.status == "CLAIMED"
    ).update({"status": "READY_TO_SEND"}, synchronize_session=False)
    
    db.commit()
    return {"status": "ok"}


@router.post("/status")
def update_sms_status(request: SmsStatusUpdateRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uuid == request.device_uuid, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    if request.message_uuid:
        sms = db.query(SmsQueue).filter(
            SmsQueue.message_uuid == request.message_uuid,
            SmsQueue.tenant_id == device.tenant_id
        ).first()
    else:
        sms = db.query(SmsQueue).filter(
            SmsQueue.id == request.sms_id,
            SmsQueue.tenant_id == device.tenant_id
        ).first()
    
    if not sms:
        raise HTTPException(status_code=404, detail="SMS not found")
        
    if request.status == "SENDING":
        sms.status = "SENDING"
        db.commit()
        return {"status": "ok"}
        
    if request.status == "FAILED":
        sms.retry_count = (sms.retry_count or 0) + 1
        if sms.retry_count > 5:
            sms.status = "FAILED"
            sms.delivery_status = "FAILED"
        else:
            sms.status = "PENDING"
            sms.processed_by_device_id = None
            sms.processing_started_at = None
    elif request.status == "SENT":
        sms.status = "COMPLETED"
        sms.delivery_status = "SENT"
    elif request.status == "DELIVERED":
        sms.status = "COMPLETED"
        sms.delivery_status = "DELIVERED"
        
    # Append immutable notification log
    log = NotificationLog(
        tenant_id=sms.tenant_id,
        channel="SMS",
        recipient=sms.recipient_phone,
        status=request.status,
        message=sms.message,
        provider_response=request.error_message or f"Status {request.status} by {device.device_name}",
        device_id=device.id
    )
    db.add(log)
    db.commit()
    return {"status": "ok"}

@router.get("/stats")
def get_sms_stats(db: Session = Depends(get_db), current_management: User = Depends(get_current_management_or_faculty)):
    today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    
    # Get sent/failed stats from NotificationLog for today in IST
    # Since logs are immutable, we only count the 'SENT' and 'FAILED' events specifically.
    log_stats = db.query(
        NotificationLog.status,
        func.count(NotificationLog.id)
    ).filter(
        NotificationLog.tenant_id == current_management.tenant_id,
        NotificationLog.channel == "SMS",
        func.date(func.timezone('Asia/Kolkata', NotificationLog.created_at)) == today_ist
    ).group_by(NotificationLog.status).all()
    
    stat_dict = {status: count for status, count in log_stats}
    sent = stat_dict.get("SENT", 0) + stat_dict.get("DELIVERED", 0)
    failed = stat_dict.get("FAILED", 0)
    
    # Get pending queue size from SmsQueue
    pending = db.query(func.count(SmsQueue.id)).filter(
        SmsQueue.tenant_id == current_management.tenant_id,
        SmsQueue.status.in_(["PENDING", "IN_PROGRESS", "CLAIMED", "READY_TO_SEND", "SENDING"])
    ).scalar() or 0
    
    return {
        "sent_today": sent,
        "failed_today": failed,
        "queue_size": pending
    }
