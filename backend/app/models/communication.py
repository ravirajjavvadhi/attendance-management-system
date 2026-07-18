from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class CampusNotice(Base):
    __tablename__ = "campus_notices"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    notice_type = Column(String, nullable=False) # CIRCULAR, ANNOUNCEMENT, EMERGENCY, HOLIDAY, EVENT
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Who did it
    event_type = Column(String, nullable=False) # CAMPUS_ENTRY, ATTENDANCE_PRESENT, ASSIGNMENT_SUBMITTED
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
