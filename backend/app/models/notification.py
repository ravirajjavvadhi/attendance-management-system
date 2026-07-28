from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class NotificationLog(Base):
    """
    Immutable Enterprise Notification & Event Stream Log.
    Never deleted from database; deleted_by_parent and read_at govern user UI state.
    """
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=True, index=True)
    
    channel = Column(String, nullable=False) # "SMS", "EMAIL", "WHATSAPP", "PUSH", "IN_APP"
    recipient = Column(String, nullable=True) # Email address, Mobile number, or push target
    status = Column(String, nullable=False, default="SENT") # "PENDING", "SENT", "FAILED", "DELIVERED"
    
    # Enterprise immutable event stream metadata
    event_type = Column(String, default="GENERAL", index=True) # ATTENDANCE, FEE, RESULT, CIRCULAR, EXAM, HOLIDAY, ASSIGNMENT, PLACEMENT, BUS, LIBRARY, ACADEMIC
    entity_type = Column(String, nullable=True) # e.g., "attendance_records", "events"
    entity_id = Column(Integer, nullable=True)
    title = Column(String, default="System Alert", nullable=False)
    message = Column(String, nullable=False) # The actual content sent
    
    provider_response = Column(String, nullable=True) # Response from Gateway or SMTP
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=True)
    
    # User read and visibility state without destructive deletion
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by_parent = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class SMSTemplate(Base):
    __tablename__ = "sms_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, unique=True)
    absent_message = Column(String, nullable=False, default="Dear Parent, {name} (Roll No: {roll_no}) is absent today.")
    late_message = Column(String, nullable=True)

