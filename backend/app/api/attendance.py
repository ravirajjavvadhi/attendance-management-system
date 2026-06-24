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
    
    from app.models.academic import Section
    # Total students in tenant (joining Section instead of User because user_id can be NULL)
    total_students = db.query(func.count(StudentProfile.id)) \
        .join(Section, StudentProfile.section_id == Section.id) \
        .filter(Section.tenant_id == current_management.tenant_id).scalar() or 0
        
    # Attendance for today
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.tenant_id == current_management.tenant_id,
        AttendanceRecord.date == today
    ).all()
    
    present_today = sum(1 for r in attendance_records if r.is_present)
    absent_today = sum(1 for r in attendance_records if not r.is_present)
    
    # Low attendance alerts (students with < 75% attendance)
    from app.models.notification import NotificationLog
    from sqlalchemy import case

    # Low attendance alerts (students with < 75% attendance)
    attendance_stats = db.query(
        StudentProfile.id,
        StudentProfile.name,
        Section.name.label("section_name"),
        func.count(AttendanceRecord.id).label("total"),
        func.sum(case((AttendanceRecord.is_present == True, 1), else_=0)).label("present")
    ).join(Section, StudentProfile.section_id == Section.id) \
     .join(AttendanceRecord, StudentProfile.id == AttendanceRecord.student_id) \
     .filter(Section.tenant_id == current_management.tenant_id) \
     .group_by(StudentProfile.id, StudentProfile.name, Section.name).all()

    alerts = []
    for stat in attendance_stats:
        if stat.total > 0:
            rate = (stat.present / stat.total) * 100
            if rate < 75:
                alerts.append({
                    "name": stat.name or f"Student #{stat.id}",
                    "class": f"Section {stat.section_name}",
                    "rate": f"{rate:.1f}%",
                    "status": "Critical" if rate < 50 else "Warning"
                })
                
    # Sort alerts so critical ones are first
    alerts.sort(key=lambda x: float(x["rate"].replace("%", "")))
    
    # Recent Notifications
    recent_logs = db.query(NotificationLog) \
        .filter(NotificationLog.tenant_id == current_management.tenant_id) \
        .order_by(NotificationLog.created_at.desc()) \
        .limit(5).all()
        
    notifications = []
    for log in recent_logs:
        notifications.append({
            "id": log.id,
            "type": log.channel, # Changed from log.type to log.channel
            "status": log.status,
            "content": log.message, # Changed from log.content to log.message
            "time": log.created_at.strftime("%I:%M %p") if log.created_at else ""
        })

    # Section-wise absent counts
    from app.models.academic import Class
    section_absent_stats = db.query(
        Class.name.label("class_name"),
        Section.name.label("section_name"),
        func.count(AttendanceRecord.id)
    ).join(Section, AttendanceRecord.section_id == Section.id) \
     .outerjoin(Class, Section.class_id == Class.id) \
     .filter(
        Section.tenant_id == current_management.tenant_id,
        AttendanceRecord.date == today,
        AttendanceRecord.is_present == False
    ).group_by(Class.name, Section.name).all()
    
    section_absent_counts = []
    for cls_name, sec_name, count in section_absent_stats:
        # Format the name based on whether class exists
        name = f"{cls_name}-{sec_name}" if cls_name else sec_name
        section_absent_counts.append({
            "section": name,
            "absent": count
        })
        
    # Sort descending by absent count
    section_absent_counts.sort(key=lambda x: x["absent"], reverse=True)

    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "attendance_rate": f"{(present_today / total_students * 100):.1f}%" if total_students > 0 else "0%",
        "alerts": alerts[:5], # top 5 lowest
        "notifications": notifications,
        "section_absent_counts": section_absent_counts
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
    
    newly_absent_ids = []
    
    for student in all_students:
        is_present = student.id not in attendance_data.absent_student_ids
        
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student.id,
            AttendanceRecord.date == attendance_data.date
        )
        if attendance_data.period is not None:
            query = query.filter(AttendanceRecord.period == attendance_data.period)
        else:
            query = query.filter(AttendanceRecord.period == None)
            
        db_record = query.first()
        
        if db_record:
            # If they were previously present, but now absent, they are newly absent!
            if db_record.is_present and not is_present:
                newly_absent_ids.append(student.id)
            
            db_record.is_present = is_present
            db_record.marked_by = current_faculty.id
        else:
            if not is_present:
                newly_absent_ids.append(student.id)
                
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=student.id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                period=attendance_data.period,
                is_present=is_present,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
    db.commit()
    
    # Trigger background SMS for newly added absentees only
    for student_id in newly_absent_ids:
        background_tasks.add_task(queue_sms, student_id, str(attendance_data.date), current_faculty.tenant_id, attendance_data.period)

    return {"message": "Smart Attendance saved successfully", "absent_count": len(newly_absent_ids)}

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
