from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
