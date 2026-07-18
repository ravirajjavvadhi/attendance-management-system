from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Time, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class Branch(Base):
    """ERP Model representing a Branch or Program (e.g., CSE, B.Com)"""
    __tablename__ = "erp_branches"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)

class Semester(Base):
    """ERP Model representing an academic term/semester"""
    __tablename__ = "erp_semesters"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("erp_branches.id"), nullable=True)
    name = Column(String, nullable=False) # e.g., "Semester 1", "Term 1"
    term_number = Column(Integer, nullable=True) # 1, 2, 3...

class Subject(Base):
    """ERP Model representing a specific subject being taught"""
    __tablename__ = "erp_subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("erp_branches.id"), nullable=True)
    semester_id = Column(Integer, ForeignKey("erp_semesters.id"), nullable=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)
    credits = Column(Integer, nullable=True, default=0)
    subject_type = Column(String, default="THEORY") # THEORY, LAB
    prerequisites = Column(String, nullable=True)
    outcomes = Column(String, nullable=True) # OBE/NBA compliance JSON or string
    is_elective = Column(Boolean, default=False)

class FacultySubjectAllocation(Base):
    """Maps which faculty is teaching which subject to which section"""
    __tablename__ = "erp_faculty_subject_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)

class Period(Base):
    """Defines the periods in a day for an institution"""
    __tablename__ = "erp_periods"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    name = Column(String, nullable=False) # e.g. "Period 1", "Lunch Break"
    period_number = Column(Integer, nullable=True) # 1, 2, 3 (null for breaks)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_break = Column(Boolean, default=False)

class DayOfWeekEnum(str, enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class Timetable(Base):
    """ERP Timetable Mapping"""
    __tablename__ = "erp_timetable"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    period_id = Column(Integer, ForeignKey("erp_periods.id"), nullable=False)
    day_of_week = Column(String, nullable=False)
    subject_id = Column(Integer, ForeignKey("erp_subjects.id"), nullable=False)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_number = Column(String, nullable=True)
