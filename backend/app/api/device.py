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


# --- MANAGEMENT ENDPOINTS ---

@router.get("/", response_model=List[DeviceResponse])
def get_devices(db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    devices = db.query(Device).filter(Device.tenant_id == current_user.tenant_id).all()
    return devices

@router.post("/generate-token", response_model=DeviceResponse)
def generate_pairing_token(request: TokenGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    # Generate a random 6 character token
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
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}


# --- ANDROID GATEWAY ENDPOINTS ---

@router.post("/register")
def register_device(request: DeviceRegisterRequest, db: Session = Depends(get_db)):
    # Find the device with the pairing token
    device = db.query(Device).filter(Device.pairing_token == request.pairing_token).first()
    if not device:
        raise HTTPException(status_code=404, detail="Invalid pairing token")
        
    # Bind the device
    device.device_uuid = request.device_uuid
    device.pairing_token = None # Clear token after use
    device.status = "ONLINE"
    device.last_seen = datetime.now(timezone.utc)
    
    # Generate a JWT for this device
    # We use a custom subject format like "device:<device_id>"
    access_token = create_access_token(subject=f"device:{device.id}")
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
    # Simple heartbeat. Ideally, protect this with JWT in the future.
    # For now, validate by device_uuid.
    device = db.query(Device).filter(Device.device_uuid == request.device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    device.battery_percentage = request.battery_percentage
    device.signal_strength = request.signal_strength
    device.sim_operator = request.sim_operator
    device.sim_slot = request.sim_slot
    device.last_seen = datetime.now(timezone.utc)
    device.status = "ONLINE"
    
    db.commit()
    return {"status": "ok"}
