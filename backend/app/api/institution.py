from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.tenant import Institution
from app.schemas.institution import InstitutionCreate, InstitutionOut, TenantProvisionRequest
from app.models.user import User, UserRole
from app.api.deps import get_current_superadmin, get_current_active_user
import re
from datetime import datetime

router = APIRouter()

@router.post("/provision", response_model=InstitutionOut)
def provision_tenant(
    request: TenantProvisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    from app.core.security import get_password_hash
    import secrets
    import string
    from app.services.notification_service import notification_service
    from app.services.email_templates import get_institution_welcome_email
    from app.core.config import settings
    
    # Generate simple subdomain
    subdomain = re.sub(r'[^a-zA-Z0-9]', '', request.name).lower()
    
    # Ensure subdomain is unique
    if db.query(Institution).filter(Institution.subdomain == subdomain).first():
        subdomain = f"{subdomain}{int(datetime.utcnow().timestamp())}"
        
    new_institution = Institution(
        name=request.name,
        subdomain=subdomain,
        type=request.type
    )
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    
    # Generate secure temporary password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    # Create management user
    admin_user = User(
        email=request.admin_email,
        tenant_id=new_institution.id,
        role=UserRole.MANAGEMENT.value,
        hashed_password=get_password_hash(temp_password)
    )
    db.add(admin_user)
    db.commit()
    
    # Send Welcome Email
    portal_url = "https://edu-flow-ai-jlr.vercel.app" # Frontend Vercel URL
    
    email_content = get_institution_welcome_email(
        management_name=request.management_name,
        institution_name=new_institution.name,
        management_email=request.admin_email,
        generated_password=temp_password,
        portal_url=portal_url
    )
    
    notification_service.send_email(
        to_email=request.admin_email,
        subject="Welcome to EduFlow AI – Your Institution Has Been Successfully Onboarded",
        html_content=email_content
    )
    
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

@router.get("/me/settings")
def read_my_institution_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    institution = db.query(Institution).filter(Institution.id == current_user.tenant_id).first()
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return {
        "periods_per_day": getattr(institution, "periods_per_day", 0),
        "notification_preference": getattr(institution, "notification_preference", "PARENT"),
        "sms_engine": getattr(institution, "sms_engine", "LEGACY"),
        "max_sms_per_device_per_day": getattr(institution, "max_sms_per_device_per_day", 70)
    }

from pydantic import BaseModel
from typing import Optional

class InstitutionSettingsUpdate(BaseModel):
    periods_per_day: Optional[int] = None
    notification_preference: Optional[str] = None
    sms_engine: Optional[str] = None
    max_sms_per_device_per_day: Optional[int] = None

@router.patch("/me/settings")
def update_my_institution_settings(
    settings: InstitutionSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    institution = db.query(Institution).filter(Institution.id == current_user.tenant_id).first()
    if institution is None:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    if settings.periods_per_day is not None:
        institution.periods_per_day = settings.periods_per_day
    if settings.notification_preference is not None:
        institution.notification_preference = settings.notification_preference
    if settings.sms_engine is not None:
        institution.sms_engine = settings.sms_engine
    if settings.max_sms_per_device_per_day is not None:
        institution.max_sms_per_device_per_day = settings.max_sms_per_device_per_day
        
    db.commit()
    return {"status": "success"}

from app.models.academic import Section
from app.models.profiles import StudentProfile
from app.models.device import Device
from app.models.notification import NotificationLog
from app.models.attendance import AttendanceRecord
from sqlalchemy.sql import func
from datetime import datetime
from zoneinfo import ZoneInfo

class DetailedInstitutionReport(BaseModel):
    id: int
    name: str
    subdomain: str
    status: str
    total_students: int
    total_faculty: int
    active_devices: int
    today_attendance_rate: str
    sms_sent_today: int

@router.get("/reports/detailed", response_model=List[DetailedInstitutionReport])
def get_detailed_institution_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    institutions = db.query(Institution).all()
    today_ist = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    
    result = []
    for inst in institutions:
        # Total Students
        total_students = db.query(func.count(StudentProfile.id)) \
            .join(Section, StudentProfile.section_id == Section.id) \
            .filter(Section.tenant_id == inst.id).scalar() or 0
            
        # Total Faculty
        total_faculty = db.query(func.count(User.id)).filter(
            User.tenant_id == inst.id, 
            User.role == UserRole.FACULTY.value
        ).scalar() or 0
        
        # Active Devices
        active_devices = db.query(func.count(Device.id)).filter(
            Device.tenant_id == inst.id,
            Device.status == "ONLINE"
        ).scalar() or 0
        
        # SMS Sent Today
        sms_sent = db.query(func.count(NotificationLog.id)).filter(
            NotificationLog.tenant_id == inst.id,
            NotificationLog.channel == "SMS",
            NotificationLog.status.in_(["SENT", "COMPLETED", "DELIVERED"]),
            func.date(func.timezone('Asia/Kolkata', NotificationLog.created_at)) == today_ist
        ).scalar() or 0
        
        # Attendance Rate Today
        total_records = db.query(func.count(AttendanceRecord.id)) \
            .join(Section, AttendanceRecord.section_id == Section.id) \
            .filter(
                Section.tenant_id == inst.id,
                AttendanceRecord.date == today_ist
            ).scalar() or 0
            
        present_records = db.query(func.count(AttendanceRecord.id)) \
            .join(Section, AttendanceRecord.section_id == Section.id) \
            .filter(
                Section.tenant_id == inst.id,
                AttendanceRecord.date == today_ist,
                AttendanceRecord.is_present == True
            ).scalar() or 0
            
        attendance_rate = "0%"
        if total_records > 0:
            rate = (present_records / total_records) * 100
            attendance_rate = f"{rate:.1f}%"
        elif total_students > 0:
            attendance_rate = "N/A" # No attendance taken yet today
            
        result.append(DetailedInstitutionReport(
            id=inst.id,
            name=inst.name,
            subdomain=inst.subdomain,
            status="Active" if inst.is_active else "Inactive",
            total_students=total_students,
            total_faculty=total_faculty,
            active_devices=active_devices,
            today_attendance_rate=attendance_rate,
            sms_sent_today=sms_sent
        ))
        
    return result

@router.delete("/{institution_id}", status_code=status.HTTP_200_OK)
def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    institution = db.query(Institution).filter(Institution.id == institution_id).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    if institution.subdomain == "system":
        raise HTTPException(status_code=400, detail="Cannot delete system tenant")
        
    from sqlalchemy import text

    # Correct FK-safe deletion order based on actual FK graph:
    # notification_logs.device_id -> devices
    # devices.tenant_id -> institutions
    # devices.user_id -> users
    # timeline_events.user_id -> users
    # All profile tables -> users
    # users.tenant_id -> institutions
    deletion_steps = [
        # Level 1a: leaf records that reference exams/assignments
        "DELETE FROM exam_results WHERE exam_id IN (SELECT id FROM exams WHERE tenant_id = :id)",
        "DELETE FROM assignment_submissions WHERE assignment_id IN (SELECT id FROM assignments WHERE tenant_id = :id)",
        # Level 1b: attendance (references students/sections)
        "DELETE FROM attendance_records WHERE tenant_id = :id",
        "DELETE FROM attendance_sessions WHERE tenant_id = :id",
        # Level 1c: notification_logs MUST come before devices (has device_id FK)
        "DELETE FROM notification_logs WHERE tenant_id = :id",
        # Level 1d: sms/comms
        "DELETE FROM sms_queue WHERE tenant_id = :id",
        "DELETE FROM campus_notices WHERE tenant_id = :id",
        # Level 1e: timeline_events MUST come before users (has user_id FK)
        "DELETE FROM timeline_events WHERE tenant_id = :id",
        "DELETE FROM calendar_days WHERE tenant_id = :id",
        "DELETE FROM semester_terms WHERE tenant_id = :id",
        # Level 1f: ERP
        "DELETE FROM erp_timetable WHERE tenant_id = :id",
        "DELETE FROM erp_faculty_subject_allocations WHERE faculty_user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        "DELETE FROM erp_periods WHERE tenant_id = :id",
        "DELETE FROM erp_subjects WHERE tenant_id = :id",
        "DELETE FROM erp_semesters WHERE tenant_id = :id",
        "DELETE FROM erp_branches WHERE tenant_id = :id",
        # Level 2: junction tables
        "DELETE FROM parent_student_links WHERE student_id IN (SELECT id FROM student_profiles WHERE section_id IN (SELECT id FROM sections WHERE tenant_id = :id))",
        "DELETE FROM parent_student_links WHERE parent_id IN (SELECT id FROM parent_profiles WHERE user_id IN (SELECT id FROM users WHERE tenant_id = :id))",
        "DELETE FROM faculty_section_assignments WHERE section_id IN (SELECT id FROM sections WHERE tenant_id = :id)",
        "DELETE FROM faculty_section_assignments WHERE faculty_user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        # Level 3: profile tables
        "DELETE FROM parent_profiles WHERE user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        "DELETE FROM faculty_profiles WHERE user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        "DELETE FROM student_profiles WHERE user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        "DELETE FROM student_profiles WHERE section_id IN (SELECT id FROM sections WHERE tenant_id = :id)",
        # Level 4: devices — MUST come after notification_logs, before users & institution
        "DELETE FROM devices WHERE user_id IN (SELECT id FROM users WHERE tenant_id = :id)",
        "DELETE FROM devices WHERE tenant_id = :id",
        # Level 5: academic structure
        "DELETE FROM exams WHERE tenant_id = :id",
        "DELETE FROM assignments WHERE tenant_id = :id",
        "DELETE FROM sections WHERE tenant_id = :id",
        "DELETE FROM classes WHERE tenant_id = :id",
        "DELETE FROM courses WHERE tenant_id = :id",
        "DELETE FROM departments WHERE tenant_id = :id",
        "DELETE FROM academic_years WHERE tenant_id = :id",
        # Level 6: institution config
        "DELETE FROM institution_modules WHERE tenant_id = :id",
        "DELETE FROM sms_templates WHERE tenant_id = :id",
        # Level 7: users — MUST be last before institution itself
        "DELETE FROM users WHERE tenant_id = :id",
    ]

    try:
        for i, query in enumerate(deletion_steps):
            sp = f"sp_del_{i}"
            try:
                db.execute(text(f"SAVEPOINT {sp}"))
                db.execute(text(query), {"id": institution_id})
                db.execute(text(f"RELEASE SAVEPOINT {sp}"))
            except Exception:
                # Roll back only this one step — previous deletions are preserved
                try:
                    db.execute(text(f"ROLLBACK TO SAVEPOINT {sp}"))
                except Exception:
                    pass

        # Re-fetch institution (ORM object may be stale after raw SQL)
        institution = db.query(Institution).filter(Institution.id == institution_id).first()
        if institution:
            db.delete(institution)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete institution: {str(e)}")
        
    return {"message": "Institution and all associated data deleted successfully"}
