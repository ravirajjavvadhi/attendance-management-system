from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
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


class ParentProfile(Base):
    __tablename__ = "parent_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    pin_hash = Column(String, nullable=True) # For 6-digit PIN login
    device_token = Column(String, nullable=True) # For Push Notifications
    biometric_enabled = Column(Boolean, default=False)
    status = Column(String, default="ACTIVE") # ACTIVE, BLOCKED, PENDING (for management approval)

class ParentStudentLink(Base):
    __tablename__ = "parent_student_links"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parent_profiles.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    relationship = Column(String, nullable=False, default="PRIMARY") # FATHER, MOTHER, GUARDIAN, BROTHER, SISTER, OTHER
    is_primary = Column(Boolean, default=False)
    receive_notifications = Column(Boolean, default=True)
    receive_sms = Column(Boolean, default=True)
    receive_push = Column(Boolean, default=True)

class FacultyComment(Base):
    __tablename__ = "faculty_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(String, nullable=True) # or DateTime
