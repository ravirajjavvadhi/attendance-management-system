from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    subdomain = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # School, Junior College, Degree College, etc.
    logo_url = Column(String, nullable=True)
    periods_per_day = Column(Integer, default=0) # 0 means daily attendance
    notification_preference = Column(String, default="PARENT") # "PARENT", "STUDENT", "BOTH"
    max_sms_per_device_per_day = Column(Integer, default=70)
    sms_engine = Column(String, default="LEGACY") # "LEGACY" or "ENTERPRISE"
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class InstitutionModules(Base):
    __tablename__ = "institution_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, unique=True)
    
    has_parent_app = Column(Boolean, default=False)
    has_student_app = Column(Boolean, default=False)
    has_fees = Column(Boolean, default=False)
    has_hostel = Column(Boolean, default=False)
    has_library = Column(Boolean, default=False)
    has_bus_tracking = Column(Boolean, default=False)
    has_placement = Column(Boolean, default=False)
    has_ai_analytics = Column(Boolean, default=False)
    has_inventory = Column(Boolean, default=False)
    has_visitor_management = Column(Boolean, default=False)
    has_alumni = Column(Boolean, default=False)
