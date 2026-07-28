from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    MEDICAL_LEAVE = "MEDICAL_LEAVE"
    ON_DUTY = "ON_DUTY"
    LEAVE = "LEAVE"
    CANCELLED = "CANCELLED"

class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    timetable_id = Column(Integer, ForeignKey("erp_timetable.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String, default="OPEN") # OPEN, LOCKED
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True)

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    period = Column(Integer, nullable=True, index=True) # For period-wise attendance
    is_present = Column(Boolean, default=True)
    status = Column(String, default=AttendanceStatusEnum.PRESENT.value) # PRESENT, ABSENT, MEDICAL_LEAVE, ON_DUTY, LEAVE, CANCELLED
    marked_by = Column(Integer, ForeignKey("users.id")) # Faculty ID
    
    # ERP Linkages & Enterprise Session Reference
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=True, index=True)
    session_id = Column(Integer, ForeignKey("attendance_sessions.id"), nullable=True, index=True)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)

# ── HIERARCHICAL MATERIALIZED REPORTING TABLES ──

class AttendanceSummary(Base):
    """
    Tier 1: Student & Subject Level Materialized Summary (StudentSummary)
    Updated asynchronously on every attendance submission for instantaneous report generation.
    """
    __tablename__ = "attendance_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=True, index=True) # Null for overall summary
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)
    month = Column(String, nullable=True) # e.g. "2023-10" or Null for semester overall
    
    total_classes = Column(Integer, default=0)
    attended_classes = Column(Integer, default=0)
    percentage = Column(Float, default=0.0) # Stored as percentage float for analytical precision
    
    # Enterprise leave counters & shortage indicators
    medical_leave_count = Column(Integer, default=0)
    od_count = Column(Integer, default=0) # On Duty count
    shortage_percentage = Column(Float, default=0.0) # E.g., if <75%, exactly how much shortage
    is_shortage = Column(Boolean, default=False) # True if total attendance < 75%

class SubjectSummary(Base):
    """Tier 2: Subject Level Materialized Summary"""
    __tablename__ = "subject_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=False, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True, index=True)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)
    
    total_sessions_conducted = Column(Integer, default=0)
    total_student_attendances = Column(Integer, default=0)
    total_presents = Column(Integer, default=0)
    average_percentage = Column(Float, default=0.0)
    shortage_student_count = Column(Integer, default=0) # Number of students with <75% attendance

class FacultySummary(Base):
    """Tier 3: Faculty Level Materialized Summary"""
    __tablename__ = "faculty_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)
    
    total_assigned_periods = Column(Integer, default=0)
    periods_completed = Column(Integer, default=0)
    pending_submissions = Column(Integer, default=0)
    attendance_completion_rate = Column(Float, default=100.0)

class DepartmentSummary(Base):
    """Tier 4: Department Level Materialized Summary"""
    __tablename__ = "department_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)
    
    total_students = Column(Integer, default=0)
    average_attendance_rate = Column(Float, default=100.0)
    best_section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    lowest_attendance_section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    shortage_student_count = Column(Integer, default=0)

class InstitutionSummary(Base):
    """Tier 5: Institution / College Level Materialized Summary"""
    __tablename__ = "institution_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True) # Daily snapshot
    
    total_students = Column(Integer, default=0)
    present_today = Column(Integer, default=0)
    absent_today = Column(Integer, default=0)
    attendance_rate = Column(Float, default=100.0)
    department_rankings_json = Column(Text, nullable=True) # JSON rankings of departments

