from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    timetable_id = Column(Integer, ForeignKey("erp_timetable.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="OPEN") # OPEN, LOCKED
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    period = Column(Integer, nullable=True, index=True) # For period-wise attendance
    is_present = Column(Boolean, default=True)
    marked_by = Column(Integer, ForeignKey("users.id")) # Faculty ID
    
    # ERP Linkages
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=True, index=True)
