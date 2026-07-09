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
    pairing_token: Optional[str] = None
    token: Optional[str] = None
    device_uuid: Optional[str] = None
    uuid: Optional[str] = None
    
    class Config:
        extra = "allow"

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
    # Free up the device UUID so the physical Android device can re-pair later without IntegrityError
    device.device_uuid = f"archived_{secrets.token_hex(4)}_{device.device_uuid}"
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

from fastapi import Request

@router.post("/register")
async def register_device(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    if not data:
        form = await request.form()
        data = dict(form)
        
    if not data:
        data = dict(request.query_params)
        
    actual_token = data.get("pairing_token") or data.get("token") or data.get("code") or data.get("pairingCode") or data.get("pairing_code")
    actual_uuid = data.get("device_uuid") or data.get("uuid") or data.get("deviceId") or data.get("device_id")
    
    if not actual_token:
        # Check if the token was sent in the URL path (fallback)
        raise HTTPException(status_code=400, detail="Missing pairing token in request")
        
    actual_token = str(actual_token).replace(" ", "").upper()
    
    device = db.query(Device).filter(Device.pairing_token == actual_token, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Invalid pairing token")
        
    final_uuid = actual_uuid or ("uuid_" + secrets.token_hex(8))
    
    # CRITICAL FIX: If the Android device's UUID is already in the DB (e.g. from an old deleted pairing that wasn't renamed, or a dirty state), 
    # we MUST rename the old record's UUID to prevent a 500 Internal Server Error (IntegrityError: unique constraint) when assigning it here!
    conflict = db.query(Device).filter(Device.device_uuid == final_uuid).first()
    if conflict and conflict.id != device.id:
        conflict.device_uuid = f"reassigned_{secrets.token_hex(4)}_{conflict.device_uuid}"
        db.commit() # Free it up
        
    device.device_uuid = final_uuid
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
async def device_heartbeat(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
    except Exception:
        data = {}
        
    if not data:
        form = await request.form()
        data = dict(form)
        
    if not data:
        data = dict(request.query_params)
        
    actual_uuid = data.get("device_uuid") or data.get("uuid") or data.get("deviceId") or data.get("device_id")
    if not actual_uuid:
        raise HTTPException(status_code=400, detail="Missing device_uuid")

    device = db.query(Device).filter(Device.device_uuid == actual_uuid, Device.status != "ARCHIVED").first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    if "battery_percentage" in data: device.battery_percentage = int(data["battery_percentage"])
    if "signal_strength" in data: device.signal_strength = int(data["signal_strength"])
    if "sim_operator" in data: device.sim_operator = str(data["sim_operator"])
    if "sim_slot" in data: device.sim_slot = int(data["sim_slot"])
    
    # Enhanced metrics
    if "is_charging" in data: device.is_charging = str(data["is_charging"]).lower() == 'true'
    if "app_version" in data: device.app_version = str(data["app_version"])
    if "foreground_service_running" in data: device.foreground_service_running = str(data["foreground_service_running"]).lower() == 'true'
    if "network_type" in data: device.network_type = str(data["network_type"])
    if "storage_remaining" in data: device.storage_remaining = str(data["storage_remaining"])
    if "ram_usage" in data: device.ram_usage = str(data["ram_usage"])
    if "android_version" in data: device.android_version = str(data["android_version"])
    
    device.last_seen = datetime.now(timezone.utc)
    device.status = "ONLINE"
    
    db.commit()
    return {"status": "ok"}
