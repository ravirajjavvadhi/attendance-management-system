from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    role: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    tenant_id: int

class UserOut(UserBase):
    id: int
    tenant_id: int
    
    class Config:
        from_attributes = True
