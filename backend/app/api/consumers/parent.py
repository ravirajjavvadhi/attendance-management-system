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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated JSON payload for the Parent App dashboard.
    Dynamically loads student details based on parent email/user mapping.
    """
    
    # Locate Parent Profile
    parent = db.query(ParentProfile).filter(ParentProfile.user_id == current_user.id).first()
    
    student_name = "Not Provided"
    student_roll = "N/A"
    section_name = "N/A"
    attendance_pct = 100.0
    total_classes = 0
    attended = 0
    
    if parent:
        link = db.query(ParentStudentLink).filter(ParentStudentLink.parent_id == parent.id).first()
        if link:
            student = db.query(StudentProfile).filter(StudentProfile.id == link.student_id).first()
            if student:
                student_name = student.name or "Student"
                student_roll = student.roll_number or "N/A"
                
                from app.models.academic import Section
                sec = db.query(Section).filter(Section.id == student.section_id).first()
                if sec:
                    section_name = sec.name
                    
                # Calculate real attendance
                from app.models.attendance import AttendanceRecord
                records = db.query(AttendanceRecord).filter(AttendanceRecord.student_id == student.id).all()
                if records:
                    total_classes = len(records)
                    attended = sum(1 for r in records if r.is_present)
                    attendance_pct = round((attended / total_classes) * 100, 1)
    
    return {
        "status": "success",
        "data": {
            "student": {
                "name": student_name,
                "roll_number": student_roll,
                "branch": "Computer Science",
                "semester": f"Section {section_name}"
            },
            "todayAttendance": {
                "status": "PRESENT" if attended > 0 else "ABSENT",
                "entry_time": "08:45 AM"
            },
            "attendancePercentage": attendance_pct,
            "notifications": [
                {"title": "Welcome", "message": f"Welcome to the portal. Monitoring {student_name}.", "date": date.today().isoformat()}
            ],
            "todayTimetable": [
                {"period": 1, "subject": "Physics", "status": "PRESENT"},
                {"period": 2, "subject": "Math", "status": "UPCOMING"}
            ],
            "assignments": [
                {"subject": "Math", "title": "Calculus Assignment 1", "due_date": "2026-07-20"}
            ],
            "examSummary": {
                "latest_exam": "Midterm 1",
                "gpa": 8.5
            },
            "quickStats": {
                "total_classes": total_classes if total_classes > 0 else 100,
                "attended": attended if total_classes > 0 else 90
            },
            "aiInsights": {
                "trend": "Positive",
                "message": f"Real-time attendance summary for {student_name} is active."
            }
        }
    }
