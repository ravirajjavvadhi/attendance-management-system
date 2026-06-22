from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InstitutionBase(BaseModel):
    name: str
    subdomain: str
    type: str
    logo_url: Optional[str] = None
    is_active: bool = True

class InstitutionCreate(InstitutionBase):
    pass

class TenantProvisionRequest(BaseModel):
    name: str
    admin_email: str

class InstitutionOut(InstitutionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
