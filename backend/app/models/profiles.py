from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True) # Nullable for quick onboarding
    name = Column(String, nullable=True)
    roll_number = Column(String, index=True)
    admission_number = Column(String, index=True, nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"))
    parent_name = Column(String, nullable=True)
    parent_mobile = Column(String, nullable=True)
    parent_email = Column(String)
    address = Column(String)
    
class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    name = Column(String, nullable=True)
    employee_id = Column(String, index=True, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    access_level = Column(String, default="ASSIGNED_SECTION_ACCESS") # "FULL_INSTITUTION_ACCESS" or "ASSIGNED_SECTION_ACCESS"

class FacultySectionAssignment(Base):
    __tablename__ = "faculty_section_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("courses.id"), nullable=True) # Future extension

