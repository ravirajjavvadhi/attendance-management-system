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

@router.get("/status", status_code=status.HTTP_200_OK)
def get_attendance_status(
    section_id: int,
    date: str,
    period: int = None,
    db: Session = Depends(get_db),
    current_faculty: User = Depends(get_current_faculty)
):
    from datetime import datetime
    try:
        query_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.section_id == section_id,
        AttendanceRecord.date == query_date
    )
    
    if period is not None:
        query = query.filter(AttendanceRecord.period == period)
        
    records = query.all()
    
    if not records:
        return {"marked": False, "records": []}
        
    return {
        "marked": True,
        "records": [
            {"student_id": r.student_id, "is_present": r.is_present}
            for r in records
        ]
    }

@router.get("/stats/today")
def get_today_stats(
    tenant_id: int = None,
    db: Session = Depends(get_db),
    current_management: User = Depends(get_current_management_or_faculty)
):
    from sqlalchemy import func
    from zoneinfo import ZoneInfo
    from datetime import datetime
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date()
    
    # SuperAdmin or Admin can specify tenant_id to view another tenant's overview
    active_tenant_id = current_management.tenant_id
    if current_management.role in ["SUPERADMIN", "ADMIN"]:
        if tenant_id:
            active_tenant_id = tenant_id
        elif active_tenant_id == 1:
            from app.models.tenant import Institution
            first_tenant = db.query(Institution).filter(Institution.subdomain != "system").first()
            if first_tenant:
                active_tenant_id = first_tenant.id
    
    from app.models.academic import Section
    # Total students in tenant (joining Section instead of User because user_id can be NULL)
    total_students = db.query(func.count(StudentProfile.id)) \
        .join(Section, StudentProfile.section_id == Section.id) \
        .filter(Section.tenant_id == active_tenant_id).scalar() or 0
        
    # Attendance for today (Only Period 1 for Morning Overview)
    attendance_records = db.query(AttendanceRecord).filter(
        AttendanceRecord.tenant_id == active_tenant_id,
        AttendanceRecord.date == today,
        AttendanceRecord.period == 1
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
     .filter(Section.tenant_id == active_tenant_id) \
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
        .filter(NotificationLog.tenant_id == active_tenant_id) \
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

    # Department-wise morning attendance (Period 1)
    from app.models.academic import Class, Department
    
    # Get all students and their departments
    all_students_dept = db.query(
        Department.name,
        func.count(StudentProfile.id)
    ).join(Section, StudentProfile.section_id == Section.id) \
     .join(Class, Section.class_id == Class.id) \
     .join(Department, Class.department_id == Department.id) \
     .filter(Section.tenant_id == active_tenant_id) \
     .group_by(Department.name).all()
     
    dept_totals = {name: count for name, count in all_students_dept}
    
    # Get present students today for period 1
    present_dept_stats = db.query(
        Department.name,
        func.count(AttendanceRecord.id)
    ).join(Section, AttendanceRecord.section_id == Section.id) \
     .join(Class, Section.class_id == Class.id) \
     .join(Department, Class.department_id == Department.id) \
     .filter(
        Section.tenant_id == active_tenant_id,
        AttendanceRecord.date == today,
        AttendanceRecord.period == 1,
        AttendanceRecord.is_present == True
    ).group_by(Department.name).all()
    
    dept_presents = {name: count for name, count in present_dept_stats}
    
    department_overview = []
    for dept_name, total in dept_totals.items():
        present = dept_presents.get(dept_name, 0)
        department_overview.append({
            "department": dept_name,
            "present": present,
            "total": total,
            "rate": round((present / total * 100), 1) if total > 0 else 0
        })
        
    department_overview.sort(key=lambda x: x["rate"])

    return {
        "total_students": total_students,
        "present_today": present_today,
        "absent_today": absent_today,
        "attendance_rate": f"{(present_today / total_students * 100):.1f}%" if total_students > 0 else "0%",
        "alerts": alerts[:5], # top 5 lowest
        "notifications": notifications,
        "department_overview": department_overview
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
    
    # Pre-fetch subject_id based on Timetable for this section and period
    subject_id = None
    if attendance_data.period is not None:
        from app.models.erp_academic import Timetable, Period
        from zoneinfo import ZoneInfo
        from datetime import datetime
        
        ist = ZoneInfo('Asia/Kolkata')
        day_name = datetime.now(ist).strftime("%A").upper()
        
        # We need period_id
        period = db.query(Period).filter(Period.period_number == attendance_data.period).first()
        if period:
            # Note: We must use the exact day of the target date, NOT today's date!
            target_date_obj = datetime.strptime(attendance_data.date, "%Y-%m-%d").date()
            target_day_name = target_date_obj.strftime("%A").upper()
            tt = db.query(Timetable).filter(
                Timetable.section_id == attendance_data.section_id,
                Timetable.period_id == period.id,
                Timetable.day_of_week == target_day_name
            ).first()
            if tt:
                subject_id = tt.subject_id
                
    subject_name = "Class"
    if subject_id:
        from app.models.erp_academic import Subject
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj:
            subject_name = subj.name
    
    
    for record in attendance_data.records:
        # Check if already exists for this date/student/period
        query = db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == record.student_id,
            AttendanceRecord.date == attendance_data.date
        )
        if attendance_data.period is not None:
            query = query.filter(AttendanceRecord.period == attendance_data.period)
        
        db_record = query.first()
        
        if db_record:
            db_record.is_present = record.is_present
            db_record.marked_by = current_faculty.id
            if subject_id:
                db_record.subject_id = subject_id
        else:
            new_record = AttendanceRecord(
                tenant_id=current_faculty.tenant_id,
                student_id=record.student_id,
                section_id=attendance_data.section_id,
                date=attendance_data.date,
                period=attendance_data.period,
                subject_id=subject_id,
                is_present=record.is_present,
                marked_by=current_faculty.id
            )
            db.add(new_record)
            
        # Add TimelineEvent
        from app.models.communication import TimelineEvent
        student_prof = db.query(StudentProfile).filter(StudentProfile.id == record.student_id).first()
        if student_prof and student_prof.user_id:
            event_type = "ATTENDANCE_PRESENT" if record.is_present else "ATTENDANCE_ABSENT"
            desc = "Marked Present" if record.is_present else "Marked Absent"
            t_event = TimelineEvent(
                tenant_id=current_faculty.tenant_id,
                user_id=student_prof.user_id,
                event_type=event_type,
                description=desc
            )
            db.add(t_event)

        if not record.is_present:
            absent_student_ids.append(record.student_id)
            
            # Send Notification to Parent!
            if student_prof and student_prof.user_id:
                from app.models.notification import NotificationLog
                from app.models.profiles import ParentStudentLink, ParentProfile
                
                # Find parent
                link = db.query(ParentStudentLink).filter(ParentStudentLink.student_id == student_prof.id).first()
                if link:
                    parent = db.query(ParentProfile).filter(ParentProfile.id == link.parent_id).first()
                    if parent:
                        parent_user = db.query(User).filter(User.id == parent.user_id).first()
                        if parent_user:
                            # Create NotificationLog for the parent
                            notif = NotificationLog(
                                tenant_id=current_faculty.tenant_id,
                                channel="PUSH",
                                recipient=parent_user.email or parent_user.mobile_number,
                                status="SENT",
                                message=f"Your child {student_prof.name} was marked ABSENT for {subject_name} on {attendance_data.date} (Period {attendance_data.period})."
                            )
                            db.add(notif)
            
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
            
        # Add TimelineEvent
        from app.models.communication import TimelineEvent
        if student.user_id:
            event_type = "ATTENDANCE_PRESENT" if is_present else "ATTENDANCE_ABSENT"
            desc = f"Marked {'Present' if is_present else 'Absent'} for period {attendance_data.period}" if attendance_data.period else f"Marked {'Present' if is_present else 'Absent'}"
            t_event = TimelineEvent(
                user_id=student.user_id,
                event_type=event_type,
                description=desc
            )
            db.add(t_event)
            
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
