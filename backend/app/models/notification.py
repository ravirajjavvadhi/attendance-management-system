from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Recipient
    type = Column(String, nullable=False) # "SMS", "EMAIL", "WHATSAPP"
    status = Column(String, nullable=False) # "PENDING", "SENT", "FAILED"
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)

class SMSTemplate(Base):
    __tablename__ = "sms_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, unique=True)
    absent_message = Column(String, nullable=False, default="Dear Parent, {name} (Roll No: {roll_no}) is absent today.")
    late_message = Column(String, nullable=True)
