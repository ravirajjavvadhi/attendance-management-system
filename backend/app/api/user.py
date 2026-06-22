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
    
    profile_data = profile_in.model_dump()
    first_name = profile_data.pop("first_name", "")
    last_name = profile_data.pop("last_name", "")
    profile_data["name"] = f"{first_name} {last_name}".strip()
    
    new_profile = FacultyProfile(**profile_data, user_id=new_user.id)
    db.add(new_profile)
    db.commit()
    
    # Send Faculty Invitation Email
    institution = db.query(Institution).filter(Institution.id == current_management.tenant_id).first()
    portal_url = "https://edu-flow-ai-jlr.vercel.app"
    
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

@router.get("/faculty", status_code=status.HTTP_200_OK)
def get_faculty_with_profiles(db: Session = Depends(get_db), current_management: User = Depends(get_current_management)):
    # Join User and FacultyProfile
    results = db.query(User, FacultyProfile).outerjoin(FacultyProfile, User.id == FacultyProfile.user_id)\
        .filter(User.tenant_id == current_management.tenant_id, User.role == UserRole.FACULTY.value).all()
        
    response = []
    for user, profile in results:
        response.append({
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "first_name": profile.name.split(" ")[0] if profile and profile.name else "",
            "last_name": " ".join(profile.name.split(" ")[1:]) if profile and profile.name and " " in profile.name else "",
            "access_level": profile.access_level if profile else "ASSIGNED_SECTION_ACCESS"
        })
    return response

@router.delete("/faculty/{user_id}", status_code=status.HTTP_200_OK)
def delete_faculty(user_id: int, db: Session = Depends(get_db), current_management: User = Depends(get_current_management)):
    user = db.query(User).filter(User.id == user_id, User.tenant_id == current_management.tenant_id, User.role == UserRole.FACULTY.value).first()
    if not user:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    if profile:
        db.delete(profile)
        
    db.delete(user)
    db.commit()
    return {"message": "Faculty revoked successfully"}

@router.put("/faculty/{user_id}", status_code=status.HTTP_200_OK)
def update_faculty(user_id: int, request: dict, db: Session = Depends(get_db), current_management: User = Depends(get_current_management)):
    user = db.query(User).filter(User.id == user_id, User.tenant_id == current_management.tenant_id, User.role == UserRole.FACULTY.value).first()
    if not user:
        raise HTTPException(status_code=404, detail="Faculty not found")
        
    profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == user.id).first()
    if profile and "access_level" in request:
        profile.access_level = request["access_level"]
        
    db.commit()
    return {"message": "Faculty updated successfully"}
