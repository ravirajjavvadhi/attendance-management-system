from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.db.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("institutions.id"), nullable=False, index=True)
    device_name = Column(String, nullable=False)
    device_uuid = Column(String, nullable=False, unique=True, index=True)
    pairing_token = Column(String, nullable=True, unique=True, index=True)
    jwt_identifier = Column(String, nullable=True, unique=True)
    
    status = Column(String, default="OFFLINE") # ONLINE, IDLE, OFFLINE, ERROR
    battery_percentage = Column(Integer, nullable=True)
    signal_strength = Column(Integer, nullable=True)
    sim_operator = Column(String, nullable=True)
    sim_slot = Column(Integer, nullable=True)
    
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
