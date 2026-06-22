from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from app.db.database import get_db
from app.models.attendance import AttendanceRecord
from app.models.user import User, UserRole
from app.models.profiles import StudentProfile
from app.schemas.attendance import AttendanceSubmit, SmartAttendanceSubmit
from app.api.deps import get_current_faculty
from app.workers.tasks import queue_sms

router = APIRouter()

@router.post("/submit")
def submit_attendance(
    attendance_data: AttendanceSubmit,
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
    
    # Trigger background tasks using Celery for absent students
    # Using delay() pushes the task to the Redis queue for the worker to pick up
    for student_id in absent_student_ids:
        queue_sms.delay(student_id, str(attendance_data.date), current_faculty.tenant_id)

    return {"message": "Attendance saved successfully", "absent_count": len(absent_student_ids)}

@router.post("/submit/smart")
def submit_smart_attendance(
    attendance_data: SmartAttendanceSubmit,
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
        queue_sms.delay(student_id, str(attendance_data.date), current_faculty.tenant_id)

    return {"message": "Smart Attendance saved successfully", "absent_count": len(attendance_data.absent_student_ids)}

@router.get("/report")
def get_attendance_report(
    section_id: int, 
    report_date: date, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_faculty)
):
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.section_id == section_id,
        AttendanceRecord.date == report_date,
        AttendanceRecord.tenant_id == current_user.tenant_id
    ).all()
    
    return records
