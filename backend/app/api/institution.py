from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.tenant import Institution
from app.schemas.institution import InstitutionCreate, InstitutionOut, TenantProvisionRequest
import re
from datetime import datetime

@router.post("/provision", response_model=InstitutionOut)
def provision_tenant(
    request: TenantProvisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    from app.core.security import get_password_hash
    
    # Generate simple subdomain
    subdomain = re.sub(r'[^a-zA-Z0-9]', '', request.name).lower()
    
    # Ensure subdomain is unique
    if db.query(Institution).filter(Institution.subdomain == subdomain).first():
        subdomain = f"{subdomain}{int(datetime.utcnow().timestamp())}"
        
    new_institution = Institution(
        name=request.name,
        subdomain=subdomain,
        type="School"
    )
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    
    # Create management user
    admin_user = User(
        email=request.admin_email,
        tenant_id=new_institution.id,
        role=UserRole.MANAGEMENT.value,
        hashed_password=get_password_hash("temporary_password_123")
    )
    db.add(admin_user)
    db.commit()
    
    return new_institution

@router.get("/with-admins")
def get_institutions_with_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    institutions = db.query(Institution).all()
    result = []
    for inst in institutions:
        admin = db.query(User).filter(User.tenant_id == inst.id, User.role == UserRole.MANAGEMENT.value).first()
        inst_dict = {
            "id": inst.id,
            "name": inst.name,
            "status": "Active" if inst.is_active else "Inactive",
            "management_email": admin.email if admin else "No Admin"
        }
        result.append(inst_dict)
    return result

@router.post("/", response_model=InstitutionOut)
def create_institution(
    institution: InstitutionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    db_institution = db.query(Institution).filter(Institution.subdomain == institution.subdomain).first()
    if db_institution:
        raise HTTPException(status_code=400, detail="Subdomain already registered")
    
    new_institution = Institution(**institution.model_dump())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return new_institution

@router.get("/", response_model=List[InstitutionOut])
def read_institutions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    institutions = db.query(Institution).offset(skip).limit(limit).all()
    return institutions

@router.get("/{institution_id}", response_model=InstitutionOut)
def read_institution(
    institution_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Enforce multi-tenant boundaries: non-superadmins can only access their own institution
    if current_user.role != UserRole.SUPERADMIN.value and current_user.tenant_id != institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to view this institution's details."
        )
        
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution
