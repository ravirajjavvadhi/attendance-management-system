from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile, FacultyProfile
from app.schemas.user import UserCreate, UserOut
from app.schemas.profile import StudentProfileCreate, FacultyProfileCreate
from app.core.security import get_password_hash
from app.api.deps import get_current_management, get_current_faculty, get_current_management_or_faculty

router = APIRouter()

@router.post("/faculty", response_model=UserOut)
def create_faculty(user_in: UserCreate, profile_in: FacultyProfileCreate, db: Session = Depends(get_db), current_management: User = Depends(get_current_management)):
    # Check if email/mobile exists
    db_user = db.query(User).filter((User.email == user_in.email) | (User.mobile_number == user_in.mobile_number)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User with this email or mobile already exists")
    
    new_user = User(
        tenant_id=current_management.tenant_id,
        email=user_in.email,
        mobile_number=user_in.mobile_number,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.FACULTY.value,
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    new_profile = FacultyProfile(**profile_in.model_dump(), user_id=new_user.id)
    db.add(new_profile)
    db.commit()
    
    return new_user

@router.post("/student", response_model=UserOut)
def create_student(user_in: UserCreate, profile_in: StudentProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_management_or_faculty)):
    # Check if email/mobile exists
    db_user = db.query(User).filter((User.email == user_in.email) | (User.mobile_number == user_in.mobile_number)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User with this email or mobile already exists")
    
    new_user = User(
        tenant_id=current_user.tenant_id,
        email=user_in.email,
        mobile_number=user_in.mobile_number,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.STUDENT.value,
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    new_profile = StudentProfile(**profile_in.model_dump(), user_id=new_user.id)
    db.add(new_profile)
    db.commit()
    
    return new_user

@router.get("/", response_model=List[UserOut])
def get_users(role: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_management: User = Depends(get_current_management)):
    query = db.query(User).filter(User.tenant_id == current_management.tenant_id)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()
