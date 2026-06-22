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
    name = Column(String, nullable=False) # e.g. "1st Year", "Class 10"

class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    name = Column(String, nullable=False) # e.g. "A", "B"
