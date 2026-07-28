from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profiles import ParentProfile, ParentStudentLink, StudentProfile
from app.core.security import create_access_token
from datetime import timedelta, date
from typing import Optional
from app.api.deps import get_current_user

router = APIRouter()

# --- Pydantic Schemas ---
class RequestOTP(BaseModel):
    mobile_number: str

class VerifyOTP(BaseModel):
    mobile_number: str
    otp: str

class LinkStudentRequest(BaseModel):
    institution_code: str
    roll_number: str
    dob: date
    relationship: str = "PRIMARY"

# --- Authentication & Linking ---

@router.post("/auth/request-otp")
def request_otp(request: RequestOTP, db: Session = Depends(get_db)):
    """
    Step 1: Request OTP for a mobile number.
    In production, this fires the Notification Engine to send an SMS.
    """
    # For now, we simulate OTP logic
    simulated_otp = "123456"
    return {"status": "success", "message": f"OTP sent to {request.mobile_number}", "mock_otp": simulated_otp}

@router.post("/auth/verify-otp")
def verify_otp(request: VerifyOTP, db: Session = Depends(get_db)):
    """
    Step 2: Verify OTP and return a JWT Token. 
    If ParentProfile doesn't exist, create it.
    """
    if request.otp != "123456":
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    user = db.query(User).filter(User.mobile_number == request.mobile_number).first()
    
    if not user:
        # Auto-provision User & ParentProfile
        user = User(
            mobile_number=request.mobile_number,
            email=f"{request.mobile_number}@parent.eduflow.local",
            role=UserRole.PARENT.value,
            is_active=True,
            tenant_id=1 # Assuming default tenant for unlinked parents, or handle dynamically
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        parent_profile = ParentProfile(user_id=user.id)
        db.add(parent_profile)
        db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/link-student")
def link_student(request: LinkStudentRequest, db: Session = Depends(get_db)): # In reality, requires current_user dependency
    """
    Step 3: One-Time Student Linking using Roll No + DOB.
    """
    # Dummy mock logic for linking
    student = db.query(StudentProfile).filter(StudentProfile.roll_number == request.roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found with provided details")
        
    # Verify DOB (Assuming dob exists on StudentProfile in future)
    # create ParentStudentLink...
    return {"status": "success", "message": "Student successfully linked to parent profile!"}

# --- Features ---

@router.get("/dashboard")
def get_parent_dashboard(
    session_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated JSON payload for the Parent App dashboard.
    Dynamically loads student details based on parent email/user mapping and optional session_id term switcher.
    """
    from app.engines.dashboard_engine import DashboardEngine
    from app.models.profiles import ParentProfile, ParentStudentLink
    from fastapi import HTTPException
    
    # Locate Parent Profile
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
        
    link = db.query(ParentStudentLink).filter(ParentStudentLink.parent_id == parent.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="No linked student found")
        
    payload = DashboardEngine.get_student_mega_payload(
        db=db,
        student_id=link.student_id,
        tenant_id=current_user.tenant_id,
        session_id=session_id
    )
    
    if not payload:
        raise HTTPException(status_code=404, detail="Student data not found")

    # Inject Parent's specific notifications if not already present from engine
    if 'notifications' not in payload or not payload['notifications']:
        from app.models.notification import NotificationLog
        db_notifs = db.query(NotificationLog).filter(
            NotificationLog.tenant_id == current_user.tenant_id,
            ((NotificationLog.recipient == current_user.email) | (NotificationLog.recipient == current_user.mobile_number) | (NotificationLog.student_id == link.student_id)),
            NotificationLog.deleted_by_parent == False
        ).order_by(NotificationLog.created_at.desc()).limit(15).all()
        
        payload['notifications'] = [
            {
                "id": n.id,
                "title": n.title or ("Attendance Alert" if "absent" in n.message.lower() else "Institutional Event"),
                "message": n.message,
                "date": n.created_at.strftime("%B %d, %I:%M %p") if n.created_at else "Recently",
                "type": n.event_type or ("ATTENDANCE" if "absent" in n.message.lower() else "GENERAL"),
                "isRead": n.is_read or False,
                "priority": "HIGH" if "absent" in n.message.lower() else "MEDIUM"
            } for n in db_notifs
        ]

    return {
        "status": "success",
        "data": payload
    }

@router.get("/profile")
def get_parent_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.profiles import ParentProfile, StudentProfile, ParentStudentLink
    from app.models.academic import Section, Class, Department
    
    parent_prof = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    if not parent_prof:
        raise HTTPException(status_code=404, detail="Parent profile not found")
        
    linked_students = []
    links = db.query(ParentStudentLink).filter(ParentStudentLink.parent_id == parent_prof.id).all()
    for link in links:
        student = db.query(StudentProfile).filter(StudentProfile.id == link.student_id).first()
        if student:
            section_name = "N/A"
            class_name = "N/A"
            dept_name = "N/A"
            if student.section_id:
                sec = db.query(Section).filter(Section.id == student.section_id).first()
                if sec:
                    section_name = sec.name
                    cls = db.query(Class).filter(Class.id == sec.class_id).first()
                    if cls:
                        class_name = cls.name
                        dept = db.query(Department).filter(Department.id == cls.department_id).first()
                        if dept:
                            dept_name = dept.name
                            
            linked_students.append({
                "id": student.id,
                "name": student.name,
                "roll_number": student.roll_number,
                "department": dept_name,
                "class": class_name,
                "section": section_name
            })
            
    return {
        "status": "success",
        "data": {
            "id": parent_prof.id,
            "name": parent_prof.name,
            "email": current_user.email,
            "mobile": current_user.mobile_number,
            "relationship": parent_prof.relationship_to_student,
            "students": linked_students
        }
    }

class LeaveRequestCreate(BaseModel):
    student_id: int
    start_date: date
    end_date: date
    reason: str

@router.post("/leaves")
def create_leave_request(
    request: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.erp_academic import LeaveRequest
    leave = LeaveRequest(
        tenant_id=current_user.tenant_id,
        student_id=request.student_id,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return {"status": "success", "data": {"id": leave.id}}

@router.get("/leaves")
def list_leave_requests(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.erp_academic import LeaveRequest
    leaves = db.query(LeaveRequest).filter(
        LeaveRequest.tenant_id == current_user.tenant_id,
        LeaveRequest.student_id == student_id
    ).all()
    return {"status": "success", "data": leaves}

@router.get("/documents")
def list_student_documents(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.erp_academic import StudentDocument
    docs = db.query(StudentDocument).filter(
        StudentDocument.tenant_id == current_user.tenant_id,
        StudentDocument.student_id == student_id
    ).all()
    return {"status": "success", "data": docs}

@router.get("/faculty")
def get_faculty_list(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.profiles import StudentProfile
    from app.models.erp_academic import FacultySubjectAllocation, Subject
    from app.models.user import User as UserModel
    
    student = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    if not student or not student.section_id:
        return {"status": "success", "data": []}
        
    allocations = db.query(FacultySubjectAllocation).filter(
        FacultySubjectAllocation.section_id == student.section_id
    ).all()
    
    results = []
    for alloc in allocations:
        subject = db.query(Subject).filter(Subject.id == alloc.subject_id).first()
        faculty = db.query(UserModel).filter(UserModel.id == alloc.faculty_user_id).first()
        if subject and faculty:
            results.append({
                "subject_name": subject.name,
                "faculty_name": faculty.full_name,
                "email": faculty.email,
                "phone": faculty.mobile_number
            })
    return {"status": "success", "data": results}

@router.get("/fees/balance")
def get_fees_balance(
    student_id: int,
    current_user: User = Depends(get_current_user)
):
    return {
        "status": "success",
        "data": {
            "total_due": 1200,
            "breakdown": {
                "Tuition": 1000,
                "Transport": 200
            }
        }
    }
