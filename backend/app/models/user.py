from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum

class UserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    MANAGEMENT = "MANAGEMENT"
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"
    PARENT = "PARENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    
    email = Column(String, index=True, nullable=True)
    mobile_number = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    
    role = Column(String, nullable=False, default=UserRole.STUDENT.value)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    institution = relationship("Institution")
