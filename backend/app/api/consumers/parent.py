from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User, UserRole
from app.models.profiles import ParentProfile, ParentStudentLink, StudentProfile
from app.core.security import create_access_token
from datetime import timedelta, date
from typing import Optional

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
def get_parent_dashboard():
    """
    Returns massive aggregated JSON payload for the Parent App dashboard.
    This guarantees the app opens instantly with only one network round-trip.
    """
    return {
        "status": "success",
        "data": {
            "student": {
                "name": "Ravi Raj",
                "roll_number": "24AG1A05L8",
                "branch": "Computer Science",
                "semester": "3rd Year, Semester 5"
            },
            "todayAttendance": {
                "status": "PRESENT",
                "entry_time": "08:45 AM"
            },
            "attendancePercentage": 92.5,
            "notifications": [
                {"title": "Fee Due", "message": "Semester 5 fees are due.", "date": "2026-07-18"}
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
                "total_classes": 120,
                "attended": 111
            },
            "aiInsights": {
                "trend": "Positive",
                "message": "Ravi's attendance in Physics has improved by 15% this month."
            }
        }
    }
