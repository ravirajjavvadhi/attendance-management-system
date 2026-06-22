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
    import secrets
    import string
    from app.services.notification_service import notification_service
    from app.services.email_templates import get_faculty_invitation_email
    from app.models.tenant import Institution
    
    # Check if email/mobile exists
    db_user = db.query(User).filter((User.email == user_in.email) | (User.mobile_number == user_in.mobile_number)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User with this email or mobile already exists")
    
    # Generate secure temporary password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    new_user = User(
        tenant_id=current_management.tenant_id,
        email=user_in.email,
        mobile_number=user_in.mobile_number,
        hashed_password=get_password_hash(temp_password),
        role=UserRole.FACULTY.value,
        is_active=user_in.is_active
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    new_profile = FacultyProfile(**profile_in.model_dump(), user_id=new_user.id)
    db.add(new_profile)
    db.commit()
    
    # Send Faculty Invitation Email
    institution = db.query(Institution).filter(Institution.id == current_management.tenant_id).first()
    portal_url = "https://attendance-management-system-afk0.onrender.com"
    
    faculty_name = f"{profile_in.first_name} {profile_in.last_name}"
    
    email_content = get_faculty_invitation_email(
        faculty_name=faculty_name,
        institution_name=institution.name if institution else "Your Institution",
        faculty_email=new_user.email,
        generated_password=temp_password,
        portal_url=portal_url
    )
    
    notification_service.send_email(
        to_email=new_user.email,
        subject="Welcome to EduFlow AI Faculty Portal",
        html_content=email_content
    )
    
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
