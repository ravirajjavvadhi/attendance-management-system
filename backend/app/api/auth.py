from datetime import timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Expects username (can be email or mobile) and password.
    """
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.mobile_number == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/mobile or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class GoogleAuthRequest(BaseModel):
    email: str
    name: Optional[str] = None
    secret: str

@router.post("/google", response_model=Token)
def login_google(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    # Verify the request is coming securely from our Next.js server
    if request.secret != settings.SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid application secret")
    
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        if request.email in ["ravirajjavvadhi@gmail.com", "ravirajjavvadi@gmail.com"]:
            # Auto-provision Super Admin
            from app.models.tenant import Institution
            from app.models.user import UserRole
            from app.core.security import get_password_hash
            
            system_tenant = db.query(Institution).filter(Institution.subdomain == "system").first()
            if not system_tenant:
                system_tenant = Institution(name="EduFlow System", subdomain="system", type="Platform")
                db.add(system_tenant)
                db.commit()
                db.refresh(system_tenant)
                
            user = User(
                email=request.email,
                tenant_id=system_tenant.id,
                role=UserRole.SUPERADMIN.value,
                hashed_password=get_password_hash("random_system_pass_123!") # Secure placeholder
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in system. Please contact your institution administrator to be onboarded."
            )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
