from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class SmsQueue(Base):
    __tablename__ = "sms_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    
    recipient_name = Column(String, nullable=True)
    recipient_phone = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    
    status = Column(String, default="PENDING", index=True) # PENDING, PROCESSING, SENT, DELIVERED, FAILED
    
    retry_count = Column(Integer, default=0)
    priority = Column(Integer, default=1) # 1 = High (Attendance), 2 = Normal (Announcements)
    source_module = Column(String, nullable=False) # ATTENDANCE, MARKS, FEES, ANNOUNCEMENTS
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
