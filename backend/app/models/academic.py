from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class AcademicYear(Base):
    __tablename__ = "academic_years"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String, nullable=False) # e.g. "2023-2024"
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    is_current = Column(Boolean, default=False)

class AcademicSession(Base):
    """
    Master controlling model representing linked academic terms/trimesters/semesters.
    Enables traversal across Semester 1 -> Semester 2 -> Semester 3 without complex lookups.
    """
    __tablename__ = "academic_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    academic_year = Column(String, nullable=False) # e.g., "2026-27"
    semester = Column(String, nullable=False) # e.g., "Semester 1", "Term 1"
    term = Column(Integer, nullable=True) # 1, 2, 3...
    status = Column(String, default="ACTIVE") # ACTIVE, ARCHIVED, UPCOMING
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    is_current = Column(Boolean, default=False)
    
    previous_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True)
    next_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String)

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    name = Column(String, nullable=False)
    
class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    name = Column(String, nullable=False) # e.g. "1st Year", "Class 10"

class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    name = Column(String, nullable=False) # e.g. "A", "B"
    admission_year = Column(Integer, nullable=True) # Used for smart year calculation (e.g., 2022)
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=False)
    
    # Enterprise extensions for priority-aware unified event engine
    category = Column(String, default="GENERAL") # EXAM, HOLIDAY, WORKSHOP, HACKATHON, SEMINAR, PLACEMENT_DRIVE, FEE_DEADLINE, RESULT, CIRCULAR, GENERAL
    priority = Column(String, default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    target_audience = Column(String, default="ALL") # ALL, STUDENTS, FACULTY, PARENTS
    academic_session_id = Column(Integer, ForeignKey("academic_sessions.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

