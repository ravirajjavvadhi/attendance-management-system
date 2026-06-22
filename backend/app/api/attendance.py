from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.db.database import get_db
from app.models.attendance import AttendanceRecord
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile
from app.schemas.attendance import AttendanceSubmit, SmartAttendanceSubmit
from app.api.deps import get_current_faculty, get_current_management_or_faculty
from app.services.sms import queue_sms

router = APIRouter()

@router.get("/stats/today")
def get_today_stats(
    db: Session = Depends(get_db),
    current_management: User = Depends(get_current_management_or_faculty)
):
    from sqlalchemy import func
    today = date.today()
    
    # Total students in tenant
    total_students = db.query(func.count(StudentProfile.id)) \
        .join(User, StudentProfile.user_id == User.id) \
        .filter(User.tenant_id == current_management.tenant_id).scalar() or 0
        
    # Attendance for today
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.tenant_id == current_management.tenant_id,
        AttendanceRecord.date == today
    ).all()
    
    present_today = sum(1 for r in attendance_records if r.is_present)
    absent_today = sum(1 for r in attendance_records if not r.is_present)
    
    # Low attendance alerts (students with < 75% attendance)
    # This requires aggregating all attendance records per student.
    # For now, we return a simple representation or mock for the alerts until we build the full reporting query.
    alerts = []
    
    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "attendance_rate": f"{(present_today / total_students * 100):.1f}%" if total_students > 0 else "0%",
        "alerts": alerts
    }

@router.post("/submit")
def submit_attendance(
    attendance_data: AttendanceSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    # Process the attendance list
    absent_student_ids = []
    
    for record in attendance_data.records:
        # Check if already exists for this date/student
        db_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == record.student_id,
            AttendanceRecord.date == attendance_data.date
        ).first()
        
        if db_record:
            db_record.is_present = record.is_present
            db_record.marked_by = current_faculty.id
        else:
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=record.student_id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                is_present=record.is_present,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
        if not record.is_present:
            absent_student_ids.append(record.student_id)
            
    db.commit()
    
    # Trigger background tasks using FastAPI for absent students
    for student_id in absent_student_ids:
        background_tasks.add_task(queue_sms, student_id, str(attendance_data.date), current_faculty.tenant_id)

    return {"message": "Attendance saved successfully", "absent_count": len(absent_student_ids)}

@router.post("/submit/smart")
def submit_smart_attendance(
    attendance_data: SmartAttendanceSubmit,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    """
    BookMyShow Style: Faculty only submits the array of absent student IDs.
    The backend automatically defaults all other students in the section to Present.
    """
    # Get all students in section
    all_students = db.query(StudentProfile).filter(StudentProfile.section_id == attendance_data.section_id).all()
    
    for student in all_students:
        is_present = student.id not in attendance_data.absent_student_ids
        
        db_record = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date == attendance_data.date
        ).first()
        
        if db_record:
            db_record.is_present = is_present
            db_record.marked_by = current_faculty.id
        else:
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=student.id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                is_present=is_present,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
    db.commit()
    
    # Trigger background SMS for absentees only
    for student_id in attendance_data.absent_student_ids:
        background_tasks.add_task(queue_sms, student_id, str(attendance_data.date), current_faculty.tenant_id)

    return {"message": "Smart Attendance saved successfully", "absent_count": len(attendance_data.absent_student_ids)}

@router.get("/report")
def get_attendance_report(
    section_id: int, 
    report_date: date, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_management_or_faculty)
):
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.section_id == section_id,
        AttendanceRecord.date == report_date,
        AttendanceRecord.tenant_id == current_user.tenant_id
    ).all()
    
    return records
@router.get("/reports/weekly")
def get_weekly_report(
    db: Session = Depends(get_db),
    current_management: User = Depends(get_current_management_or_faculty)
):
    """
    Returns the attendance rate for the last 5 days (e.g., Mon-Fri).
    """
    from datetime import timedelta
    from sqlalchemy import func
    
    today = date.today()
    days = []
    for i in range(4, -1, -1):
        day = today - timedelta(days=i)
        
        # Get total records for this day
        records = db.query(AttendanceRecord).filter(
            AttendanceRecord.tenant_id == current_management.tenant_id,
            AttendanceRecord.date == day
        ).all()
        
        total = len(records)
        present = sum(1 for r in records if r.is_present)
        rate = int((present / total * 100)) if total > 0 else 0
        
        days.append({
            "name": day.strftime("%a"), # Mon, Tue, etc
            "attendance": rate
        })
        
    return days
