from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.device import Device
from app.models.user import User
from app.api.deps import get_current_management_or_faculty, get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import secrets
from app.core.security import create_access_token

router = APIRouter()

# Schema for Management generating a token
class TokenGenerateRequest(BaseModel):
    device_name: str

class DeviceResponse(BaseModel):
    id: int
    device_name: str
    status: str
    battery_percentage: Optional[int]
    signal_strength: Optional[int]
    sim_operator: Optional[str]
    last_seen: Optional[datetime]
    pairing_token: Optional[str]

    class Config:
        orm_mode = True

# Schema for Android Device Registering
class DeviceRegisterRequest(BaseModel):
    pairing_token: str
    device_uuid: str

class DeviceHeartbeatRequest(BaseModel):
    device_uuid: str
    battery_percentage: int
    signal_strength: int
    sim_operator: Optional[str] = None
    sim_slot: Optional[int] = None
    is_charging: Optional[bool] = None
    app_version: Optional[str] = None
    foreground_service_running: Optional[bool] = None
    network_type: Optional[str] = None
    storage_remaining: Optional[str] = None
    ram_usage: Optional[str] = None
    android_version: Optional[str] = None

class DeviceRenameRequest(BaseModel):
    device_name: str


# --- MANAGEMENT ENDPOINTS ---

@router.get("/", response_model=List[DeviceResponse])
def get_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    # Don't show archived devices in the main list
    devices = db.query(Device).filter(Device.tenant_id == current_user.tenant_id, Device.status != "ARCHIVED").all()
    return devices

@router.post("/generate-token", response_model=DeviceResponse)
def generate_pairing_token(request: TokenGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    token = secrets.token_hex(3).upper()
    
    new_device = Device(
        tenant_id=current_user.tenant_id,
        device_name=request.device_name,
        device_uuid="pending_" + secrets.token_hex(4),
        pairing_token=token,
        status="IDLE"
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.delete("/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    device = db.query(Device).filter(Device.id == device_id, Device.tenant_id == current_user.tenant_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    # Soft delete
    device.status = "ARCHIVED"
    device.pairing_token = None
    device.jwt_identifier = None
    db.commit()
    return {"message": "Device archived successfully"}

@router.patch("/{device_id}")
def rename_device(device_id: int, request: DeviceRenameRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    device = db.query(Device).filter(Device.id == device_id, Device.tenant_id == current_user.tenant_id, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.device_name = request.device_name
    db.commit()
    return {"message": "Device renamed successfully"}


# --- ANDROID GATEWAY ENDPOINTS ---

@router.post("/register")
def register_device(request: DeviceRegisterRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.pairing_token == request.pairing_token, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Invalid pairing token")
        
    device.device_uuid = request.device_uuid
    device.pairing_token = None
    device.status = "ONLINE"
    device.last_seen = datetime.now(timezone.utc)
    
    access_token = create_access_token(data={"sub": f"device:{device.id}"})
    device.jwt_identifier = access_token
    
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "tenant_id": device.tenant_id,
        "device_id": device.id
    }

@router.post("/heartbeat")
def device_heartbeat(request: DeviceHeartbeatRequest, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.device_uuid == request.device_uuid, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device.battery_percentage = request.battery_percentage
    device.signal_strength = request.signal_strength
    device.sim_operator = request.sim_operator
    device.sim_slot = request.sim_slot
    
    # Enhanced metrics
    if request.is_charging is not None: device.is_charging = request.is_charging
    if request.app_version: device.app_version = request.app_version
    if request.foreground_service_running is not None: device.foreground_service_running = request.foreground_service_running
    if request.network_type: device.network_type = request.network_type
    if request.storage_remaining: device.storage_remaining = request.storage_remaining
    if request.ram_usage: device.ram_usage = request.ram_usage
    if request.android_version: device.android_version = request.android_version
    
    device.last_seen = datetime.now(timezone.utc)
    device.status = "ONLINE"
    
    db.commit()
    return {"status": "ok"}
